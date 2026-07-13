# SPDX-FileCopyrightText: 2022-2024 CERN.
# SPDX-License-Identifier: MIT

"""Awards datastreams tests."""

from copy import deepcopy

import pytest
from invenio_access.permissions import system_identity

from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.awards.datastreams import (
    AwardsServiceWriter,
    CORDISAwardsServiceWriter,
    CORDISProjectTransformer,
    OpenAIREProjectTransformer,
)
from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import TransformerError, WriterError
from invenio_vocabularies.datastreams.readers import XMLReader


@pytest.fixture(scope="function")
def dict_award_entry():
    return StreamEntry(
        {
            "acronym": "TA",
            "code": "0751743",
            "enddate": "2010-09-30",
            "funding": [
                {
                    "fundingStream": {
                        "description": "Directorate for Geosciences - Division of "
                        "Ocean Sciences",
                        "id": "NSF::GEO/OAD::GEO/OCE",
                    },
                    "jurisdiction": "US",
                    "name": "National Science Foundation",
                    "shortName": "NSF",
                }
            ],
            "h2020programme": [],
            "id": "nsf_________::3eb1b4f6d6e251a19f9fdeed2aab88d8",
            "openaccessmandatefordataset": False,
            "openaccessmandateforpublications": False,
            "startdate": "2008-04-01",
            "subject": ["Oceanography"],
            "title": "Test title",
            "websiteurl": "https://test.com",
        }
    )


@pytest.fixture(scope="function")
def dict_award_entry_ec():
    """Full award data."""
    return StreamEntry(
        {
            "acronym": "TS",
            "code": "129123",
            "enddate": "2025-12-31",
            "funding": [
                {
                    "fundingStream": {
                        "description": "Test stream",
                        "id": "TST::test::test",
                    },
                    "jurisdiction": "GR",
                    "name": "Test Name",
                    "shortName": "TST",
                }
            ],
            "h2020programme": [],
            "id": "40|corda__h2020::000000000000000000",
            "openaccessmandatefordataset": False,
            "openaccessmandateforpublications": False,
            "startdate": "2008-04-01",
            "subject": ["Oceanography"],
            "title": "Test title",
            "websiteurl": "https://test.com",
        }
    )


@pytest.fixture(scope="function")
def expected_from_award_json():
    return {
        "id": "021nxhr62::0751743",
        "identifiers": [{"identifier": "https://test.com", "scheme": "url"}],
        "number": "0751743",
        "program": "GEO/OAD",
        "title": {"en": "Test title"},
        "funder": {"id": "021nxhr62"},
        "acronym": "TA",
    }


@pytest.fixture(scope="function")
def expected_from_award_json_ec():
    return {
        "id": "00k4n6c32::129123",
        "identifiers": [
            {"identifier": "https://cordis.europa.eu/projects/129123", "scheme": "url"}
        ],
        "number": "129123",
        "title": {"en": "Test title"},
        "funder": {"id": "00k4n6c32"},
        "acronym": "TS",
        "program": "test",
    }


CORDIS_PROJECT_XML = bytes(
    """
<project
	xmlns="http://cordis.europa.eu">
	<language>en</language>
	<availableLanguages readOnly="true">en</availableLanguages>
	<rcn>264556</rcn>
	<id>101117736</id>
	<acronym>Time2SWITCH</acronym>
	<identifiers>
		<grantDoi>10.3030/101117736</grantDoi>
	</identifiers>
	<relations>
		<associations>
			<organization type="coordinator" source="corda" order="1" ecContribution="1496795" terminated="false" sme="false" netEcContribution="1496795" totalCost="1496795">
				<availableLanguages readOnly="true">en</availableLanguages>
				<rcn>1908489</rcn>
				<id>999979888</id>
				<vatNumber>ATU37675002</vatNumber>
				<legalName>TECHNISCHE UNIVERSITAET WIEN</legalName>
				<shortName>TU WIEN</shortName>
				<departmentName>Institute of Electrodynamics, Microwave and Circuit Engineer</departmentName>
				<relations>
					<categories>
						<category classification="organizationActivityType" type="relatedOrganizationActivityType">
							<language>en</language>
							<availableLanguages readOnly="true">de,en,es,fr,it,pl</availableLanguages>
							<code>HES</code>
							<title>Higher or Secondary Education Establishments</title>
							<displayCode readOnly="true">/Higher or Secondary Education Establishments</displayCode>
						</category>
					</categories>
				</relations>
			</organization>
			<programme source="corda" uniqueProgrammePart="true" type="relatedLegalBasis">
				<code>HORIZON.1.1</code>
			</programme>
			<programme source="corda" type="relatedLegalBasis">
				<code>ANOTHER.CODE.WHICH.IS.NOT.THE.UNIQUE.PROGRAMME.PART</code>
			</programme>
			<programme source="corda" type="relatedTopic">
				<code>ERC-2023-STG</code>
				<frameworkProgramme>HORIZON</frameworkProgramme>
			</programme>
		</associations>
		<categories>
			<category classification="euroSciVoc" type="isInFieldOfScience">
				<language>en</language>
				<availableLanguages readOnly="true">de,en,es,fr,it,pl</availableLanguages>
				<code>/21/39/225</code>
				<title>oncology</title>
				<displayCode readOnly="true">/medical and health sciences/clinical medicine/oncology</displayCode>
			</category>
		</categories>
	</relations>
</project>
    """,
    encoding="utf-8",
)


@pytest.fixture(scope="module")
def expected_from_cordis_project_xml():
    return {
        "id": "00k4n6c32::101117736",
        "program": "HORIZON.1.1",
        "subjects": [{"id": "euroscivoc:225"}],
        "organizations": [{"name": "TECHNISCHE UNIVERSITAET WIEN"}],
    }


def test_awards_transformer(app, dict_award_entry, expected_from_award_json):
    """Test the OpenAIREProjectTransformer's output against expected award data."""
    transformer = OpenAIREProjectTransformer()
    assert expected_from_award_json == transformer.apply(dict_award_entry).entry


def test_awards_service_writer_create(
    app, search_clear, example_funder_ec, award_full_data
):
    """Verify creation of an award record and match it with expected data."""
    awards_writer = AwardsServiceWriter()
    award_rec = awards_writer.write(StreamEntry(award_full_data))
    award_dict = award_rec.entry.to_dict()

    award_full_data["funder"]["name"] = example_funder_ec["name"]
    assert dict(award_dict, **award_full_data) == award_dict

    # not-ideal cleanup
    award_rec.entry._record.delete(force=True)


def test_awards_funder_id_not_exist(
    app, search_clear, example_funder, example_funder_ec, award_full_data_invalid_id
):
    """Ensure writing an award with an invalid funder ID raises an error."""
    awards_writer = AwardsServiceWriter()
    with pytest.raises(WriterError) as err:
        awards_writer.write(StreamEntry(award_full_data_invalid_id))
    expected_error = [
        {
            "InvalidRelationValue": "Invalid value {funder_id}.".format(
                funder_id=award_full_data_invalid_id.get("funder").get("id")
            )
        }
    ]

    assert expected_error in err.value.args


def test_awards_funder_id_not_exist_no_funders(
    app, search_clear, award_full_data_invalid_id
):
    """Check error on writing an award with no valid funders."""
    awards_writer = AwardsServiceWriter()
    with pytest.raises(WriterError) as err:
        awards_writer.write(StreamEntry(award_full_data_invalid_id))
    expected_error = [
        {
            "InvalidRelationValue": "Invalid value {funder_id}.".format(
                funder_id=award_full_data_invalid_id.get("funder").get("id")
            )
        }
    ]

    assert expected_error in err.value.args


def test_awards_transformer_ec_functionality(
    app,
    search_clear,
    dict_award_entry,
    dict_award_entry_ec,
    expected_from_award_json,
    expected_from_award_json_ec,
):
    """Test transformer output for standard and EC-specific awards."""
    transformer = OpenAIREProjectTransformer()

    assert expected_from_award_json == transformer.apply(dict_award_entry).entry
    assert expected_from_award_json_ec == transformer.apply(dict_award_entry_ec).entry


def test_awards_service_writer_duplicate(
    app, search_clear, example_funder_ec, award_full_data
):
    """Verify error on attempting to create a duplicate award."""
    writer = AwardsServiceWriter()
    award_rec = writer.write(stream_entry=StreamEntry(award_full_data))
    Award.index.refresh()  # refresh index to make changes live
    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=StreamEntry(award_full_data))

    expected_error = [f"Vocabulary entry already exists: {award_full_data}"]
    assert expected_error in err.value.args

    # not-ideal cleanup
    award_rec.entry._record.delete(force=True)


def test_awards_service_writer_update_existing(
    app, search_clear, example_funder_ec, award_full_data, service
):
    """Check updating an existing award record with new data."""
    writer = AwardsServiceWriter(update=True)
    orig_award_rec = writer.write(stream_entry=StreamEntry(award_full_data))
    Award.index.refresh()  # refresh index to make changes live
    updated_award = deepcopy(award_full_data)
    updated_award["title"] = {"en": "New Test title"}
    _ = writer.write(stream_entry=StreamEntry(updated_award))
    award_rec = service.read(system_identity, orig_award_rec.entry.id)
    award_dict = award_rec.to_dict()

    updated_award["funder"]["name"] = example_funder_ec["name"]
    assert _.entry.id == orig_award_rec.entry.id
    assert dict(award_dict, **updated_award) == award_dict

    # not-ideal cleanup
    award_rec._record.delete(force=True)


def test_awards_service_writer_update_non_existing(
    app, search_clear, example_funder_ec, award_full_data, service
):
    """Test updating a non-existing award, creating a new record."""
    updated_award = deepcopy(award_full_data)
    updated_award["title"] = {"en": "New Test title"}
    writer = AwardsServiceWriter(update=True)
    award_rec = writer.write(stream_entry=StreamEntry(updated_award))
    award_rec = service.read(system_identity, award_rec.entry.id)
    award_dict = award_rec.to_dict()

    updated_award["funder"]["name"] = example_funder_ec["name"]
    assert dict(award_dict, **updated_award) == award_dict

    # not-ideal cleanup
    award_rec._record.delete(force=True)


def test_awards_cordis_transformer(app, expected_from_cordis_project_xml):
    """Validate transformation of CORDIS project XML to expected format."""
    reader = XMLReader()
    award = next(reader.read(CORDIS_PROJECT_XML))

    cordis_transformer = CORDISProjectTransformer(pic_mapping={})
    transformed_award_data = cordis_transformer.apply(StreamEntry(award["project"]))

    assert transformed_award_data.entry == expected_from_cordis_project_xml


def test_awards_cordis_transformer_resolves_pic_to_ror(app):
    """When the PIC is in the resolution map, the org becomes a ROR-id relation."""
    reader = XMLReader()
    award = next(reader.read(CORDIS_PROJECT_XML))

    pic_mapping = {"999979888": "04d836q62"}
    cordis_transformer = CORDISProjectTransformer(pic_mapping=pic_mapping)
    transformed = cordis_transformer.apply(StreamEntry(award["project"]))

    assert transformed.entry["organizations"] == [{"id": "04d836q62"}]


def test_awards_cordis_transformer_unresolved_pic_keeps_name_only(app):
    """Unresolved PICs are stored by name only (no `id`, so `PIDListRelation` won't resolve them)."""
    reader = XMLReader()
    award = next(reader.read(CORDIS_PROJECT_XML))

    cordis_transformer = CORDISProjectTransformer(
        pic_mapping={"other-pic": "01abc1234"}
    )
    transformed = cordis_transformer.apply(StreamEntry(award["project"]))

    assert transformed.entry["organizations"] == [
        {"name": "TECHNISCHE UNIVERSITAET WIEN"}
    ]


PIC_MAPPING_CSV = """\
pic,ror_id,confidence,source
111,01high1111,high,openaire_direct
222,02med22222,medium,openaire_external
333,03review33,review,participant_name_country
444,04manual44,manual,manual_override
555,,high,openaire_direct
,06nopic666,high,openaire_direct
"""


def test_load_pic_mapping_filters_confidence(tmp_path):
    """Rows with confidence not in the accepted set are dropped."""
    csv_path = tmp_path / "pic_mapping.csv"
    csv_path.write_text(PIC_MAPPING_CSV)

    params = CORDISProjectTransformer.pic_mapping_params
    mapping = CORDISProjectTransformer._load_pic_mapping(
        str(csv_path),
        filename=params["filename"],
        accepted_confidence=params["accepted_confidence"],
    )

    assert mapping == {"111": "01high1111", "222": "02med22222", "444": "04manual44"}


def test_load_pic_mapping_missing_file_raises(tmp_path):
    """Missing mapping CSV is a hard error; fail fast on misconfiguration."""
    params = CORDISProjectTransformer.pic_mapping_params
    with pytest.raises(TransformerError):
        CORDISProjectTransformer._load_pic_mapping(
            str(tmp_path / "pic_mapping.csv"),
            filename=params["filename"],
            accepted_confidence=params["accepted_confidence"],
        )


@pytest.fixture(scope="function")
def example_euroscivoc_subject(db, identity):
    """euroscivoc:225 subject required by the CORDIS test XML."""
    from invenio_records_resources.proxies import current_service_registry

    from invenio_vocabularies.contrib.subjects.api import Subject

    subjects_service = current_service_registry.get("subjects")
    subject = subjects_service.create(
        identity,
        {
            "id": "euroscivoc:225",
            "scheme": "EuroSciVoc",
            "subject": "oncology",
        },
    )
    Subject.index.refresh()
    yield subject
    subject._record.delete(force=True)
    db.session.commit()


def test_cordis_datastream_end_to_end_pic_resolves(
    app,
    db,
    search_clear,
    service,
    identity,
    example_funder_ec,
    example_affiliation,
    example_euroscivoc_subject,
    tmp_path,
):
    """End-to-end CORDIS update: PIC -> ROR map loaded from local config,
    transformer emits a vocabulary relation, writer updates the award, and
    the read view dereferences `organizations` against the affiliations vocab.
    """
    # Baseline award (CORDIS is update-only).
    baseline_id = "00k4n6c32::101117736"
    service.create(
        identity,
        {
            "id": baseline_id,
            "number": "101117736",
            "title": {"en": "Time2SWITCH"},
            "funder": {"id": "00k4n6c32"},
        },
    )
    Award.index.refresh()

    # Local PIC -> ROR map: PIC from CORDIS_PROJECT_XML resolves to the
    # `example_affiliation` ROR id (01ggx4157, CERN).
    csv_path = tmp_path / "pic_mapping.csv"
    csv_path.write_text(
        "pic,ror_id,confidence,source\n" "999979888,01ggx4157,high,openaire_direct\n"
    )
    app.config["VOCABULARIES_AWARDS_PIC_MAPPING_SOURCE"] = str(csv_path)

    # Run the real readers/transformer/writer chain on the fixture XML.
    award = next(XMLReader().read(CORDIS_PROJECT_XML))
    transformer = CORDISProjectTransformer()
    writer = CORDISAwardsServiceWriter()
    transformed = transformer.apply(StreamEntry(award["project"]))
    writer.write(transformed)
    Award.index.refresh()

    read_item = service.read(identity, baseline_id)
    assert read_item["organizations"] == [
        {
            "id": "01ggx4157",
            "name": "CERN",
            "identifiers": [{"identifier": "01ggx4157", "scheme": "ror"}],
        }
    ]
