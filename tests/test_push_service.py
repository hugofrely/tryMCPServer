import pytest

from app.schemas import PushJobResponse
from app.services import PushService
from app.services.contact_matching_service import MatchResult
from app.services.push_service import SyncResult


class TestPushService:
    """Tests for PushService."""

    @pytest.fixture
    def service(
        self,
        mock_push_job_repo,
        mock_contact_repo,
        mock_hubspot_client,
        mock_matching_service,
    ) -> PushService:
        """Create PushService with mocked dependencies."""
        return PushService(
            push_job_repo=mock_push_job_repo,
            contact_repo=mock_contact_repo,
            hubspot_client=mock_hubspot_client,
            matching_service=mock_matching_service,
        )

    # =========================================================================
    # create_push_job tests
    # =========================================================================

    class TestCreatePushJob:
        """Tests for create_push_job method."""

        @pytest.fixture
        def service(
            self,
            mock_push_job_repo,
            mock_contact_repo,
            mock_hubspot_client,
            mock_matching_service,
        ) -> PushService:
            return PushService(
                push_job_repo=mock_push_job_repo,
                contact_repo=mock_contact_repo,
                hubspot_client=mock_hubspot_client,
                matching_service=mock_matching_service,
            )

        @pytest.mark.parametrize(
            "profiles,expected_count",
            [
                ([], 0),
                ([{"first_name": "John"}], 1),
                (
                    [
                        {"first_name": "John", "email": "john@example.com"},
                        {"first_name": "Jane", "email": "jane@example.com"},
                    ],
                    2,
                ),
                (
                    [{"first_name": f"User{i}"} for i in range(5)],
                    5,
                ),
            ],
            ids=["empty", "single", "two_profiles", "five_profiles"],
        )
        def test_creates_contacts_for_profiles(
            self,
            service: PushService,
            mock_contact_repo,
            profiles: list,
            expected_count: int,
        ):
            """Should create correct number of contacts."""
            service.create_push_job(profiles)

            mock_contact_repo.bulk_create.assert_called_once()
            call_args = mock_contact_repo.bulk_create.call_args[0][0]
            assert len(call_args) == expected_count

        def test_creates_pending_job(self, service: PushService, mock_push_job_repo):
            """Should create a pending job."""
            result = service.create_push_job([{"first_name": "John"}])

            mock_push_job_repo.create_pending_job.assert_called_once()
            assert result.status == "pending"

        def test_returns_push_job_response(self, service: PushService):
            """Should return PushJobResponse."""
            result = service.create_push_job([])

            assert isinstance(result, PushJobResponse)
            assert result.id == 1

    # =========================================================================
    # process_job tests
    # =========================================================================

    class TestProcessJob:
        """Tests for process_job method."""

        @pytest.fixture
        def service(
            self,
            mock_push_job_repo,
            mock_contact_repo,
            mock_hubspot_client,
            mock_matching_service,
        ) -> PushService:
            return PushService(
                push_job_repo=mock_push_job_repo,
                contact_repo=mock_contact_repo,
                hubspot_client=mock_hubspot_client,
                matching_service=mock_matching_service,
            )

        def test_raises_if_job_not_found(
            self, service: PushService, mock_push_job_repo
        ):
            """Should raise ValueError if job not found."""
            mock_push_job_repo.get_by_id.return_value = None

            with pytest.raises(ValueError, match="Job 999 not found"):
                service.process_job(999)

        def test_fetches_hubspot_contacts(
            self, service: PushService, mock_hubspot_client
        ):
            """Should fetch all HubSpot contacts."""
            service.process_job(1)

            mock_hubspot_client.get_all_contacts.assert_called_once()

        def test_uses_matching_service(
            self,
            service: PushService,
            mock_matching_service,
            mock_contact_repo,
            mock_hubspot_client,
            make_contact,
        ):
            """Should use matching service to match contacts."""
            local_contacts = [make_contact(email="john@example.com")]
            hubspot_contacts = [{"id": "hs_1", "properties": {}}]

            mock_contact_repo.get_by_job_id.return_value = local_contacts
            mock_hubspot_client.get_all_contacts.return_value = hubspot_contacts

            service.process_job(1)

            mock_matching_service.match_contacts.assert_called_once_with(
                local_contacts=local_contacts,
                hubspot_contacts=hubspot_contacts,
            )

        @pytest.mark.parametrize(
            "matched_count,unmatched_count,expected_updated,expected_created",
            [
                (0, 0, 0, 0),
                (1, 0, 1, 0),
                (0, 1, 0, 1),
                (2, 3, 2, 3),
            ],
            ids=["no_contacts", "only_matched", "only_unmatched", "mixed"],
        )
        def test_sync_counts(
            self,
            service: PushService,
            mock_matching_service,
            mock_hubspot_client,
            make_contact,
            make_hubspot_contact,
            matched_count: int,
            unmatched_count: int,
            expected_updated: int,
            expected_created: int,
        ):
            """Should return correct sync counts."""
            matched = [
                (make_contact(id=i), make_hubspot_contact(id=f"hs_{i}"))
                for i in range(matched_count)
            ]
            unmatched = [
                make_contact(id=100 + i) for i in range(unmatched_count)
            ]
            mock_matching_service.match_contacts.return_value = MatchResult(
                matched=matched, unmatched=unmatched
            )

            result = service.process_job(1)

            assert result.updated_count == expected_updated
            assert result.created_count == expected_created

        def test_creates_contact_in_hubspot_for_unmatched(
            self,
            service: PushService,
            mock_matching_service,
            mock_hubspot_client,
            make_contact,
        ):
            """Should create new contacts in HubSpot for unmatched."""
            unmatched = make_contact(first_name="New", email="new@example.com")
            mock_matching_service.match_contacts.return_value = MatchResult(
                matched=[], unmatched=[unmatched]
            )

            service.process_job(1)

            mock_hubspot_client.create_contact.assert_called_once()

        def test_updates_contact_in_hubspot_for_matched(
            self,
            service: PushService,
            mock_matching_service,
            mock_hubspot_client,
            make_contact,
            make_hubspot_contact,
        ):
            """Should update existing contacts in HubSpot for matched."""
            matched_contact = make_contact(email="existing@example.com")
            hubspot_contact = make_hubspot_contact(id="hs_1", email="existing@example.com")
            mock_matching_service.match_contacts.return_value = MatchResult(
                matched=[(matched_contact, hubspot_contact)], unmatched=[]
            )

            service.process_job(1)

            mock_hubspot_client.update_contact.assert_called_once()

        def test_marks_job_completed_on_success(
            self, service: PushService, mock_push_job_repo
        ):
            """Should mark job as completed on success."""
            service.process_job(1)

            mock_push_job_repo.mark_as_completed.assert_called_once_with(
                job_id=1, created_count=0, updated_count=0
            )
            mock_push_job_repo.commit.assert_called()

        def test_marks_job_failed_on_error(
            self, service: PushService, mock_push_job_repo, mock_hubspot_client
        ):
            """Should mark job as failed on error."""
            mock_hubspot_client.get_all_contacts.side_effect = Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                service.process_job(1)

            mock_push_job_repo.rollback.assert_called_once()
            mock_push_job_repo.mark_as_failed.assert_called_once()
            assert "API Error" in mock_push_job_repo.mark_as_failed.call_args[0][1]

        def test_returns_sync_result(self, service: PushService):
            """Should return SyncResult dataclass."""
            result = service.process_job(1)

            assert isinstance(result, SyncResult)
            assert hasattr(result, "created_count")
            assert hasattr(result, "updated_count")

        def test_updates_local_contact_with_hubspot_id(
            self,
            service: PushService,
            mock_matching_service,
            mock_contact_repo,
            mock_hubspot_client,
            make_contact,
        ):
            """Should update local contact with HubSpot ID after create."""
            unmatched = make_contact(id=42, email="test@example.com")
            mock_matching_service.match_contacts.return_value = MatchResult(
                matched=[], unmatched=[unmatched]
            )
            mock_hubspot_client.create_contact.return_value = {"id": "hubspot_999"}

            service.process_job(1)

            mock_contact_repo.update_with_hubspot_data.assert_called_once()
            call_kwargs = mock_contact_repo.update_with_hubspot_data.call_args[1]
            assert call_kwargs["contact_id"] == 42
            assert call_kwargs["hubspot_id"] == "hubspot_999"

    # =========================================================================
    # get_job_status tests
    # =========================================================================

    class TestGetJobStatus:
        """Tests for get_job_status method."""

        @pytest.fixture
        def service(
            self,
            mock_push_job_repo,
            mock_contact_repo,
            mock_hubspot_client,
            mock_matching_service,
        ) -> PushService:
            return PushService(
                push_job_repo=mock_push_job_repo,
                contact_repo=mock_contact_repo,
                hubspot_client=mock_hubspot_client,
                matching_service=mock_matching_service,
            )

        @pytest.mark.parametrize(
            "job_exists,expected_none",
            [
                (True, False),
                (False, True),
            ],
            ids=["job_exists", "job_not_found"],
        )
        def test_returns_job_or_none(
            self,
            service: PushService,
            mock_push_job_repo,
            make_push_job,
            job_exists: bool,
            expected_none: bool,
        ):
            """Should return job if exists, None otherwise."""
            mock_push_job_repo.get_by_id.return_value = (
                make_push_job() if job_exists else None
            )

            result = service.get_job_status(1)

            assert (result is None) == expected_none
