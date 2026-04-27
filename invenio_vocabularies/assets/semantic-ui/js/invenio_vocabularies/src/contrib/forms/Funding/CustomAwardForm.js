// This file is part of InvenioVocabularies
// Copyright (C) 2021-2024 CERN.
// Copyright (C) 2021 Northwestern University.
// Copyright (C) 2026 ZBW – Leibniz-Informationszentrum Wirtschaft.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React from "react";
import { Form, Header } from "semantic-ui-react";
import { TextField, RemoteSelectField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_vocabularies/i18next";
import _isEmpty from "lodash/isEmpty";
import { Field, getIn } from "formik";

import Overridable from "react-overridable";

function CustomAwardForm({ deserializeFunder, selectedFunding }) {
  function deserializeFunderToDropdown(funderItem) {
    const funderName = funderItem?.name;
    const funderPID = funderItem?.id;
    const funderCountry = funderItem?.country_name ?? funderItem?.country;

    if (!funderName && !funderPID) {
      return {};
    }
    const isVocabFunder = funderPID;
    const funderText = [funderName, funderCountry, funderPID]
      .filter(Boolean)
      .join(", ");

    const dropdownContent = isVocabFunder ? (
      <div className="ui header">
        {funderName} (
        <span>
          <a
            href={`https://ror.org/${funderPID}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              alt={i18next.t("ROR logo")}
              src="/static/images/ror-icon.svg"
              className="inline-id-icon mr-5"
            />
            {funderPID}
          </a>
        </span>
        ){funderCountry && <div className="sub header">{funderCountry}</div>}
      </div>
    ) : null;

    return {
      id: funderPID,
      // Used when selected
      text: funderText,
      // Used in dropdown list
      content: dropdownContent || funderText,
      value: funderPID || funderName,
      key: funderPID || funderName,
      ...(funderName && { name: funderName }),
      ...(funderPID && { pid: funderPID }),
    };
  }
  function serializeFunderFromDropdown(funderDropObject) {
    const isVocabFunder = funderDropObject.id;

    let result;
    if (isVocabFunder) {
      result = {
        id: funderDropObject.id,
        name: funderDropObject.name,
        ...(funderDropObject.name && { name: funderDropObject.name }),
        ...(funderDropObject.pid && { pid: funderDropObject.pid }),
      };
    } else {
      result = {
        name: funderDropObject.name,
      };
    }
    return result;
  }

  return (
    <Form>
      <Field name="selectedFunding.funder">
        {({ form: { values, setFieldValue } }) => {
          const currentFunder = getIn(values, "selectedFunding.funder");

          const initialSuggestions = currentFunder
            ? [deserializeFunderToDropdown(currentFunder)]
            : [];

          return (
            <Overridable
              id="InvenioVocabularies.CustomAwardForm.RemoteSelectField.Container"
              fieldPath="selectedFunding.funder"
            >
              <RemoteSelectField
                fieldPath="selectedFunding.funder"
                suggestionAPIUrl="/api/funders"
                suggestionAPIHeaders={{
                  Accept: "application/vnd.inveniordm.v1+json",
                }}
                placeholder={i18next.t("Search or create funder")}
                serializeSuggestions={(funders) => {
                  return funders.map((funder) =>
                    deserializeFunderToDropdown(deserializeFunder(funder))
                  );
                }}
                initialSuggestions={initialSuggestions}
                searchInput={{
                  autoFocus: _isEmpty(selectedFunding),
                }}
                label={i18next.t("Funder")}
                noQueryMessage={i18next.t("Search for funder...")}
                clearable
                allowAdditions
                multiple={false}
                selectOnBlur={false}
                selectOnNavigation={false}
                required
                value={currentFunder?.id || currentFunder?.name || ""}
                isFocused={currentFunder ? false : true}
                onValueChange={({ formikProps }, selectedFundersArray) => {
                  if (selectedFundersArray.length === 1) {
                    const selectedFunder = selectedFundersArray[0];
                    if (selectedFunder) {
                      const deserializedFunder =
                        serializeFunderFromDropdown(selectedFunder);
                      formikProps.form.setFieldValue(
                        "selectedFunding.funder",
                        deserializedFunder
                      );
                    }
                  } else {
                    setFieldValue("selectedFunding.funder", undefined);
                  }
                }}
              />
            </Overridable>
          );
        }}
      </Field>
      <Overridable id="InvenioVocabularies.CustomAwardForm.AwardInformationHeader.Container">
        <Header as="h3" size="small">
          {i18next.t("Additional information")} ({i18next.t("optional")})
        </Header>
      </Overridable>
      <Form.Group widths="equal">
        <Overridable
          id="InvenioVocabularies.CustomAwardForm.AwardNumberTextField.Container"
          fieldPath="selectedFunding.award.number"
        >
          <TextField
            label={i18next.t("Number")}
            placeholder={i18next.t("Award/Grant number")}
            fieldPath="selectedFunding.award.number"
          />
        </Overridable>
        <Overridable
          id="InvenioVocabularies.CustomAwardForm.AwardTitleTextField.Container"
          fieldPath="selectedFunding.award.title"
        >
          <TextField
            label={i18next.t("Title")}
            placeholder={i18next.t("Award/Grant Title")}
            fieldPath="selectedFunding.award.title"
          />
        </Overridable>
        <Overridable
          id="InvenioVocabularies.CustomAwardForm.AwardUrlTextField.Container"
          fieldPath="selectedFunding.award.url"
        >
          <TextField
            label={i18next.t("URL")}
            placeholder={i18next.t("Award/Grant URL")}
            fieldPath="selectedFunding.award.url"
          />
        </Overridable>
      </Form.Group>
    </Form>
  );
}

CustomAwardForm.propTypes = {
  deserializeFunder: PropTypes.func.isRequired,
  selectedFunding: PropTypes.object,
};

CustomAwardForm.defaultProps = {
  selectedFunding: undefined,
};

export default CustomAwardForm;
