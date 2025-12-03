from typing import List, TypedDict

from fastapi import FastAPI, HTTPException

from app.async_task_executor import AsyncTaskExecutor
from app.database import Session, engine
from app.hubspot_client import HubSpotClient
from app.models import Base
from app.repositories import ContactRepository, PushJobRepository
from app.schemas import ContactCreate

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRM Push API")
hubspot = HubSpotClient()

task_executor = AsyncTaskExecutor()
task_executor.add_task(
    "process_push_job",
    lambda job_id: process_push_job(job_id),
)


class Profile(TypedDict):
    first_name: str = None
    last_name: str = None
    email: str = None
    linkedin_id: str = None
    phone: str = None
    company: str = None


class PushRequest(TypedDict):
    profiles: List[Profile]


def process_push_job(job_id: str):
    job_id_int = int(job_id)

    # Create session and repositories
    session = Session()
    push_job_repo = PushJobRepository(session)
    contact_repo = ContactRepository(session)

    try:
        # Verify job exists
        push_job = push_job_repo.get_by_id(job_id_int)
        if not push_job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Retrieve contacts for this job
        job_contacts = contact_repo.get_by_job_id(job_id_int)

        # Step 1: Pull all contacts from HubSpot
        hubspot_contacts = hubspot.get_all_contacts()

        # Step 2: Match profiles to existing contacts
        matched_contacts = []
        new_profiles = []

        for profile_contact in job_contacts:
            matched = False
            matched_hubspot_contact = None

            for hubspot_contact in hubspot_contacts:
                if matched:
                    break

                # 1. Try to match by LinkedIn ID
                if (
                    not matched
                    and profile_contact.linkedin_id
                    and hubspot_contact["properties"].get("linkedin_id")
                    == profile_contact.linkedin_id
                ):
                    matched_hubspot_contact = hubspot_contact
                    matched = True
                # 2. Try to match by email
                elif (
                    not matched
                    and profile_contact.email
                    and hubspot_contact["properties"].get("email") == profile_contact.email
                ):
                    matched_hubspot_contact = hubspot_contact
                    matched = True
                # 3. Try to match by first_name + last_name
                elif (
                    not matched and profile_contact.first_name and profile_contact.last_name
                ):
                    hubspot_first = (
                        hubspot_contact["properties"].get("firstname", "").lower()
                    )
                    hubspot_last = hubspot_contact["properties"].get("lastname", "").lower()
                    if (
                        hubspot_first == profile_contact.first_name.lower()
                        and hubspot_last == profile_contact.last_name.lower()
                    ):
                        matched_hubspot_contact = hubspot_contact
                        matched = True

            # Process the match if found
            if matched and matched_hubspot_contact:
                matched_contacts.append((profile_contact, matched_hubspot_contact))
            else:
                new_profiles.append(profile_contact)

        # Step 4: Update existing contacts in HubSpot
        updated_count = 0
        for profile_contact, matched_hubspot_contact in matched_contacts:
            contact_data = {
                "first_name": profile_contact.first_name
                or matched_hubspot_contact["properties"].get("firstname"),
                "last_name": profile_contact.last_name
                or matched_hubspot_contact["properties"].get("lastname"),
                "email": profile_contact.email
                or matched_hubspot_contact["properties"].get("email"),
                "linkedin_id": profile_contact.linkedin_id
                or matched_hubspot_contact["properties"].get("linkedin_id"),
                "phone": profile_contact.phone
                or matched_hubspot_contact["properties"].get("phone"),
                "company": profile_contact.company
                or matched_hubspot_contact["properties"].get("company"),
            }

            hubspot_id = matched_hubspot_contact["id"]
            # Update in HubSpot
            hubspot.update_contact(hubspot_id, contact_data)

            # Update contact using repository
            contact_repo.update_with_hubspot_data(
                contact_id=profile_contact.id,
                hubspot_id=hubspot_id,
                first_name=contact_data["first_name"],
                last_name=contact_data["last_name"],
                email=contact_data["email"],
                linkedin_id=contact_data["linkedin_id"],
                phone=contact_data["phone"],
                company=contact_data["company"],
            )
            updated_count += 1

        # Step 5: Create new contacts in HubSpot
        created_count = 0
        for profile_contact in new_profiles:
            contact_data = {
                "first_name": profile_contact.first_name,
                "last_name": profile_contact.last_name,
                "email": profile_contact.email,
                "linkedin_id": profile_contact.linkedin_id,
                "phone": profile_contact.phone,
                "company": profile_contact.company,
            }

            # Create in HubSpot
            hubspot_contact = hubspot.create_contact(contact_data)

            # Update contact using repository
            contact_repo.update_with_hubspot_data(
                contact_id=profile_contact.id,
                hubspot_id=hubspot_contact["id"],
                first_name=contact_data["first_name"],
                last_name=contact_data["last_name"],
                email=contact_data["email"],
                linkedin_id=contact_data["linkedin_id"],
                phone=contact_data["phone"],
                company=contact_data["company"],
            )
            created_count += 1

        # Mark job as completed using repository
        push_job_repo.mark_as_completed(
            job_id=job_id_int,
            created_count=created_count,
            updated_count=updated_count
        )

        # Commit all changes
        session.commit()

    except Exception as e:
        session.rollback()
        # Mark job as failed
        push_job_repo.mark_as_failed(job_id_int, str(e))
        session.commit()
        raise
    finally:
        session.close()


@app.post("/push")
async def push_profiles(request: dict):
    """
    Main endpoint: takes a list of profiles and starts a push job.
    """
    request_data = PushRequest(**request)

    with Session.begin() as session:
        push_job_repo = PushJobRepository(session)
        contact_repo = ContactRepository(session)

        # Create pending job
        push_job = push_job_repo.create_pending_job()
        job_id = str(push_job.id)

        # Create contacts for the job
        profiles = request_data.get("profiles", [])
        contact_schemas = [
            ContactCreate(
                job_id=push_job.id,
                first_name=profile.get("first_name"),
                last_name=profile.get("last_name"),
                email=profile.get("email"),
                linkedin_id=profile.get("linkedin_id"),
                phone=profile.get("phone"),
                company=profile.get("company"),
            )
            for profile in profiles
        ]
        contact_repo.bulk_create(contact_schemas)

    task_executor.execute("process_push_job", job_id)
    return {"job_id": job_id}


@app.get("/push/{job_id}")
async def get_push_status(job_id: str):
    """Get the status of a push job"""
    with Session() as session:
        push_job_repo = PushJobRepository(session)
        job = push_job_repo.get_by_id(int(job_id))

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        response = {
            "job_id": job_id,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        }

        if job.status == "completed":
            response["created"] = job.created_count or 0
            response["updated"] = job.updated_count or 0
        elif job.status == "failed":
            response["error"] = job.error or "Unknown error"

        return response


@app.get("/health")
async def health():
    return {"status": "ok"}
