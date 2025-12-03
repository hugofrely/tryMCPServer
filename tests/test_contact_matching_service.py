import pytest

from app.domain import HubSpotContact, MatchResult
from app.services.contact_matching_service import ContactMatchingService


class TestContactMatchingService:
    """Tests for ContactMatchingService."""

    @pytest.fixture
    def service(self) -> ContactMatchingService:
        return ContactMatchingService()

    # =========================================================================
    # Match by different criteria (parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        "local_attrs,hubspot_attrs,description",
        [
            # LinkedIn ID matching (priority 1)
            (
                {"linkedin_id": "linkedin_123"},
                {"linkedin_id": "linkedin_123"},
                "linkedin_id",
            ),
            # Email matching (priority 2)
            (
                {"email": "test@example.com"},
                {"email": "test@example.com"},
                "email",
            ),
            # Name matching (priority 3)
            (
                {"first_name": "John", "last_name": "Doe"},
                {"firstname": "John", "lastname": "Doe"},
                "full_name",
            ),
            # Name matching case insensitive
            (
                {"first_name": "JOHN", "last_name": "DOE"},
                {"firstname": "john", "lastname": "doe"},
                "full_name_case_insensitive",
            ),
        ],
        ids=["linkedin_id", "email", "full_name", "full_name_case_insensitive"],
    )
    def test_match_contacts_by_criteria(
        self,
        service: ContactMatchingService,
        make_contact,
        make_hubspot_contact,
        local_attrs: dict,
        hubspot_attrs: dict,
        description: str,
    ):
        """Should match contacts by various criteria."""
        local = make_contact(**local_attrs)
        hubspot = make_hubspot_contact(**hubspot_attrs)

        result = service.match_contacts([local], [hubspot])

        assert len(result.matched) == 1, f"Failed to match by {description}"
        assert len(result.unmatched) == 0
        assert result.matched[0][0].id == local.id
        assert result.matched[0][1].id == hubspot.id

    # =========================================================================
    # No match scenarios (parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        "local_attrs,hubspot_attrs,description",
        [
            # Different emails
            (
                {"email": "unique@example.com"},
                {"email": "different@example.com"},
                "different_emails",
            ),
            # Partial name (only first name)
            (
                {"first_name": "John", "last_name": None},
                {"firstname": "John", "lastname": "Doe"},
                "partial_name_first_only",
            ),
            # Partial name (only last name)
            (
                {"first_name": None, "last_name": "Doe"},
                {"firstname": "John", "lastname": "Doe"},
                "partial_name_last_only",
            ),
            # Different linkedin IDs
            (
                {"linkedin_id": "linkedin_123"},
                {"linkedin_id": "linkedin_456"},
                "different_linkedin_ids",
            ),
        ],
        ids=["different_emails", "partial_name_first", "partial_name_last", "different_linkedin"],
    )
    def test_no_match_scenarios(
        self,
        service: ContactMatchingService,
        make_contact,
        make_hubspot_contact,
        local_attrs: dict,
        hubspot_attrs: dict,
        description: str,
    ):
        """Should not match contacts when criteria don't align."""
        local = make_contact(**local_attrs)
        hubspot = make_hubspot_contact(**hubspot_attrs)

        result = service.match_contacts([local], [hubspot])

        assert len(result.matched) == 0, f"Should not match for {description}"
        assert len(result.unmatched) == 1

    # =========================================================================
    # Priority tests
    # =========================================================================

    def test_linkedin_takes_priority_over_email(
        self, service: ContactMatchingService, make_contact, make_hubspot_contact
    ):
        """LinkedIn ID should take priority over email for matching."""
        local = make_contact(linkedin_id="linkedin_123", email="wrong@example.com")
        hubspot_linkedin = make_hubspot_contact(
            id="hs_linkedin", linkedin_id="linkedin_123", email="other@example.com"
        )
        hubspot_email = make_hubspot_contact(id="hs_email", email="wrong@example.com")

        result = service.match_contacts([local], [hubspot_linkedin, hubspot_email])

        assert len(result.matched) == 1
        assert result.matched[0][1].id == "hs_linkedin"

    def test_email_takes_priority_over_name(
        self, service: ContactMatchingService, make_contact, make_hubspot_contact
    ):
        """Email should take priority over name for matching."""
        local = make_contact(
            email="test@example.com", first_name="Wrong", last_name="Name"
        )
        hubspot_email = make_hubspot_contact(
            id="hs_email", email="test@example.com", firstname="Other", lastname="Person"
        )
        hubspot_name = make_hubspot_contact(
            id="hs_name", firstname="Wrong", lastname="Name"
        )

        result = service.match_contacts([local], [hubspot_email, hubspot_name])

        assert len(result.matched) == 1
        assert result.matched[0][1].id == "hs_email"

    # =========================================================================
    # Edge cases (parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        "local_contacts,hubspot_count,expected_matched,expected_unmatched",
        [
            # Empty local contacts
            ([], 1, 0, 0),
            # Empty hubspot contacts
            ([{"email": "test@example.com"}], 0, 0, 1),
            # Both empty
            ([], 0, 0, 0),
        ],
        ids=["empty_local", "empty_hubspot", "both_empty"],
    )
    def test_empty_lists(
        self,
        service: ContactMatchingService,
        make_contact,
        make_hubspot_contact,
        local_contacts: list,
        hubspot_count: int,
        expected_matched: int,
        expected_unmatched: int,
    ):
        """Should handle empty contact lists."""
        locals_list = [make_contact(**c) for c in local_contacts]
        hubspot_list = [make_hubspot_contact() for _ in range(hubspot_count)]

        result = service.match_contacts(locals_list, hubspot_list)

        assert len(result.matched) == expected_matched
        assert len(result.unmatched) == expected_unmatched

    # =========================================================================
    # Multiple contacts
    # =========================================================================

    def test_multiple_contacts_mixed_results(
        self, service: ContactMatchingService, make_contact, make_hubspot_contact
    ):
        """Should correctly categorize multiple contacts."""
        locals_list = [
            make_contact(id=1, email="match@example.com"),
            make_contact(id=2, email="nomatch@example.com"),
            make_contact(id=3, linkedin_id="linkedin_456"),
        ]
        hubspot_list = [
            make_hubspot_contact(id="hs_1", email="match@example.com"),
            make_hubspot_contact(id="hs_2", linkedin_id="linkedin_456"),
        ]

        result = service.match_contacts(locals_list, hubspot_list)

        assert len(result.matched) == 2
        assert len(result.unmatched) == 1
        assert result.unmatched[0].id == 2

    # =========================================================================
    # Return type
    # =========================================================================

    def test_returns_match_result_dataclass(self, service: ContactMatchingService):
        """Should return MatchResult dataclass."""
        result = service.match_contacts([], [])

        assert isinstance(result, MatchResult)
        assert hasattr(result, "matched")
        assert hasattr(result, "unmatched")
