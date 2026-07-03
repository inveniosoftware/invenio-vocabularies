/*
 * SPDX-FileCopyrightText: 2021-2024 CERN.
 * SPDX-FileCopyrightText: 2021 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { Segment } from "semantic-ui-react";
import { i18next } from "@translations/invenio_vocabularies/i18next";

export function NoAwardResults({ switchToCustom }) {
  return (
    <Segment
      basic
      content={
        <p>
          {i18next.t("Did not find your award/grant? ")}
          <a
            href="/"
            onClick={(e) => {
              e.preventDefault();
              switchToCustom();
            }}
          >
            {i18next.t("Add a custom award/grant.")}
          </a>
        </p>
      }
    />
  );
}

NoAwardResults.propTypes = {
  switchToCustom: PropTypes.func.isRequired,
};
