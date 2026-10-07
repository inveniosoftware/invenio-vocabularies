/*
 * SPDX-FileCopyrightText: 2021-2023 CERN.
 * SPDX-FileCopyrightText: 2021 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_vocabularies/i18next";
import { useRef } from "react";
import { useDrag, useDrop } from "react-dnd";
import { Button, Icon, Label, List } from "semantic-ui-react";

import FundingModal from "./FundingModal";
import PropTypes from "prop-types";

export const FundingFieldItem = ({
  compKey = undefined,
  index = undefined,
  fundingItem = undefined,
  awardType = undefined,
  moveFunding,
  replaceFunding,
  removeFunding,
  searchConfig,
  deserializeAward,
  deserializeFunder,
  computeFundingContents,
}) => {
  const dropRef = useRef(null);
  // eslint-disable-next-line no-unused-vars
  const [_, drag, preview] = useDrag({
    item: { index, type: "award" },
  });
  const [{ hidden }, drop] = useDrop({
    accept: "award",
    hover(item, monitor) {
      if (!dropRef.current) {
        return;
      }
      const dragIndex = item.index;
      const hoverIndex = index;

      // Don't replace items with themselves
      if (dragIndex === hoverIndex) {
        return;
      }

      if (monitor.isOver({ shallow: true })) {
        moveFunding(dragIndex, hoverIndex);
        item.index = hoverIndex;
      }
    },
    collect: (monitor) => ({
      hidden: monitor.isOver({ shallow: true }),
    }),
  });

  let { headerContent, descriptionContent, awardOrFunder } =
    computeFundingContents(fundingItem);

  // Initialize the ref explicitely
  drop(dropRef);
  return (
    <List.Item
      ref={dropRef}
      key={compKey}
      className={hidden ? "deposit-drag-listitem hidden" : "deposit-drag-listitem"}
    >
      <List.Content floated="right">
        <Button size="mini" type="button" onClick={() => removeFunding(index)}>
          {i18next.t("Remove")}
        </Button>
        <FundingModal
          searchConfig={searchConfig}
          onAwardChange={(selectedFunding) => {
            replaceFunding(index, selectedFunding);
          }}
          mode={awardType}
          action="edit"
          trigger={
            <Button size="mini" primary type="button">
              {i18next.t("Edit")}
            </Button>
          }
          deserializeAward={deserializeAward}
          deserializeFunder={deserializeFunder}
          computeFundingContents={computeFundingContents}
          initialFunding={fundingItem}
        />
      </List.Content>

      <List.Icon ref={drag} name="bars" className="drag-anchor" />
      <List.Content ref={preview}>
        <List.Header>
          <>
            <span className="mr-5">{headerContent}</span>

            {awardOrFunder === "award"
              ? fundingItem?.award?.number && (
                  <Label basic size="mini" className="mr-5">
                    {fundingItem.award.number}
                  </Label>
                )
              : ""}
            {awardOrFunder === "award"
              ? fundingItem?.award?.url && (
                  <a
                    href={`${fundingItem.award.url}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={i18next.t("Open external link")}
                  >
                    <Icon link name="external alternate" />
                  </a>
                )
              : ""}
          </>
        </List.Header>
        <List.Description>
          {descriptionContent ? descriptionContent : <br />}
        </List.Description>
      </List.Content>
    </List.Item>
  );
};

FundingFieldItem.propTypes = {
  compKey: PropTypes.any,
  index: PropTypes.number,
  fundingItem: PropTypes.object,
  awardType: PropTypes.string,
  moveFunding: PropTypes.func.isRequired,
  replaceFunding: PropTypes.func.isRequired,
  removeFunding: PropTypes.func.isRequired,
  searchConfig: PropTypes.object.isRequired,
  deserializeAward: PropTypes.func.isRequired,
  deserializeFunder: PropTypes.func.isRequired,
  computeFundingContents: PropTypes.func.isRequired,
};
