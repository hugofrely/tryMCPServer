import pytest

from app.domain import JobNotFoundError, MatchResult, SyncResult
from app.schemas import PushJobResponse
from app.services import PushService


class TestPushService:
    """Tests for PushService."""

    @pytest.fixture
    def service(
        self,
        mock_uow,
        mock_crm_client,
        mock_matching_service,
    ) -> PushService:
        """Create PushService with mocked dependencies."""
        return PushService(
            uow=mock_uow,
            crm_client=mock_crm_client,
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
            mock_uow,
            mock_crm_client,
            mock_matching_service,
        ) -> PushService:
            return PushService(
                uow=mock_uow,
                crm_client=mock_crm_client,
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
            mock_uow,
            profiles: list,
            expected_count: int,
        ):
            """Should create correct number of contacts."""
            service.create_push_job(profiles)

            mock_uow.contacts.bulk_create.assert_called_once()
            call_args = mock_uow.contacts.bulk_create.call_args[0][0]
            assert len(call_args) == expected_count

        def test_creates_pending_job(self, service: PushService, mock_uow):
            """Should create a pending job."""
            result = service.create_push_job([{"first_name": "John"}])

            mock_uow.push_jobs.create_pending_job.assert_called_once()
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
            mock_uow,
            mock_crm_client,
            mock_matching_service,
        ) -> PushService:
            return PushService(
                uow=mock_uow,
                crm_client=mock_crm_client,
                matching_service=mock_matching_service,
            )

        def test_raises_job_not_found_error(
            self, service: PushService, mock_uow
        ):
            """Should raise JobNotFoundError if job not found."""
            mock_uow.push_jobs.get_by_id.return_value = None

            with pytest.raises(JobNotFoundError) as exc_info:
                service.process_job(999)

            assert exc_info.value.job_id == 999
            assert "999" in exc_info.value.message

        def test_fetches_hubspot_contacts(
            self, service: PushService, mock_crm_client
        ):
            """Should fetch all HubSpot contacts."""
            service.process_job(1)

            mock_crm_client.get_all_contacts.assert_called_once()

        def test_uses_matching_service(
            self,
            service: PushService,
            mock_matching_service,
            mock_uow,
            mock_crm_client,
            make_contact,
            make_hubspot_contact,
        ):
            """Should use matching service to match contacts."""
            local_contacts = [make_contact(email="john@example.com")]
            hubspot_contacts = [make_hubspot_contact()]

            mock_uow.contacts.get_by_job_id.return_value = local_contacts
            mock_crm_client.get_all_contacts.return_value = hubspot_contacts

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
            mock_crm_client,
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
            mock_crm_client,
            make_contact,
        ):
            """Should create new contacts in HubSpot for unmatched."""
            unmatched = make_contact(first_name="New", email="new@example.com")
            mock_matching_service.match_contacts.return_value = MatchResult(
                matched=[], unmatched=[unmatched]
            )

            service.process_job(1)

            mock_crm_client.create_contact.assert_called_once()

        def test_updates_contact_in_hubspot_for_matched(
            self,
            service: PushService,
            mock_matching_service,
            mock_crm_client,
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

            mock_crm_client.update_contact.assert_called_once()

        def test_marks_job_completed_on_success(
            self, service: PushService, mock_uow
        ):
            """Should mark job as completed on success."""
            service.process_job(1)

            mock_uow.push_jobs.mark_as_completed.assert_called_once_with(
                job_id=1, created_count=0, updated_count=0
            )

        def test_marks_job_failed_on_error(
            self, service: PushService, mock_uow, mock_crm_client
        ):
            """Should mark job as failed on error."""
            mock_crm_client.get_all_contacts.side_effect = Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                service.process_job(1)

            mock_uow.push_jobs.mark_as_failed.assert_called_once()
            assert "API Error" in mock_uow.push_jobs.mark_as_failed.call_args[0][1]

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
            mock_uow,
            mock_crm_client,
            make_contact,
            make_hubspot_contact,
        ):
            """Should update local contact with HubSpot ID after create."""
            unmatched = make_contact(id=42, email="test@example.com")
            mock_matching_service.match_contacts.return_value = MatchResult(
                matched=[], unmatched=[unmatched]
            )
            mock_crm_client.create_contact.return_value = make_hubspot_contact(id="hubspot_999")

            service.process_job(1)

            mock_uow.contacts.update_with_hubspot_data.assert_called_once()
            call_kwargs = mock_uow.contacts.update_with_hubspot_data.call_args[1]
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
            mock_uow,
            mock_crm_client,
            mock_matching_service,
        ) -> PushService:
            return PushService(
                uow=mock_uow,
                crm_client=mock_crm_client,
                matching_service=mock_matching_service,
            )

        def test_returns_job_if_exists(
            self,
            service: PushService,
            mock_uow,
            make_push_job,
        ):
            """Should return job if it exists."""
            expected_job = make_push_job()
            mock_uow.push_jobs.get_by_id.return_value = expected_job

            result = service.get_job_status(1)

            assert result == expected_job

        def test_raises_job_not_found_error(
            self,
            service: PushService,
            mock_uow,
        ):
            """Should raise JobNotFoundError if job not found."""
            mock_uow.push_jobs.get_by_id.return_value = None

            with pytest.raises(JobNotFoundError) as exc_info:
                service.get_job_status(999)

            assert exc_info.value.job_id == 999
