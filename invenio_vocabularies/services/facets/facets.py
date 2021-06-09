# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary facets."""

from bisect import bisect, bisect_left

from elasticsearch_dsl import AttrDict
from invenio_records_resources.services.records.facets import TermsFacet


class LabellingBucket(AttrDict):
    """Bucket class to allow label extration."""

    def __init__(self, key, doc_count):
        """Constructor."""
        super().__init__({"key": key, "doc_count": doc_count})


class NestedVocabularyTermsFacet(TermsFacet):
    """A term facet for vocabularies with nested/hierarchical labelling."""

    def __init__(self, splitchar="-", **kwargs):
        """Initialize the nested vocabulary terms facet."""
        self._splitchar = splitchar
        super().__init__(**kwargs)

    def _build_nested_buckets(self, buckets):
        """Build nested buckets from a vocabulary facet.

        This function will return a flattened list of buckets. The input
        will be a list of ES buckets with, potentially, a nested key.
        That means, dash separated values (e.g. image-drawing). The output
        be [image, image-drawing], so the parent (i.e. image) of the nested
        aggregation is also queried to ES (to get the UI label).
        In addition, it will calculate the aggregated value of the parent
        doc_count.

        For example, doc_count in parenthesis:
        bucket.data = [
            image-png(2), image-jpg(5), publication(3), publication-book(1)
        ]
        buckets_out = [
            image(7), image-jpg(5), image-png(2),
            publication(4), publication-book(1)
        ]
        """
        seen = set()
        buckets_idx = []  # avoid implementing __lt__ for bisect on buckets
        buckets_out = []  # sorted, non duplicates buckets
        for bucket in buckets:
            key = self.get_value(bucket)
            metric = self.get_metric(bucket)
            nested = key.split(self._splitchar)

            root = ""
            for facet in nested[:-1]:
                root = facet if not root else root + "-" + facet
                if root not in seen:
                    seen.add(root)
                    idx = bisect(buckets_idx, root)
                    buckets_out.insert(idx, LabellingBucket(root, metric))
                    buckets_idx.insert(idx, root)  # add root to idx
                else:  # update aggregated count
                    idx = bisect_left(buckets_idx, root)
                    buckets_out[idx].doc_count += metric

            if key not in seen:  # Add the last bucket
                seen.add(key)
                idx = bisect(buckets_idx, key)
                buckets_out.insert(idx, bucket)
                buckets_idx.insert(idx, key)  # add full key to idx

        return buckets_out

    def _build_bucket_out(self, bucket, label_map, key_prefix, filter_values):
        """Build a single bucket output."""
        key = full_key = bucket.key
        if key_prefix:
            full_key = key_prefix + self._splitchar + full_key

        bucket_out = {
            "key": key,
            "doc_count": self.get_metric(bucket),
            "label": label_map[key],
            "is_selected": self.is_filtered(full_key, filter_values)
        }

        return bucket_out

    def _build_bucket_list(
        self, buckets, label_map, key_prefix, filter_values,
        idx=0, inner=False
    ):
        """Recursively builds bucket dictionary."""
        # check the test_facets.py::test_nested_vocabulary_facet_labelling
        # to see an example ouput of the function call
        buckets_out = []
        bucket = buckets[idx]
        bucket_out = self._build_bucket_out(
            bucket, label_map, key_prefix, filter_values)

        buckets_inner = []
        while idx+1 < len(buckets):
            if bucket.key in buckets[idx+1].key:  # is a child
                idx, bucket_inner = self._build_bucket_list(
                    buckets, label_map, key_prefix, filter_values, idx+1, True)
                buckets_inner.extend(bucket_inner)
            elif inner:  # finish the children cycle
                break
            else:  # add current root and get next
                if buckets_inner:
                    bucket_out["inner"] = {'buckets': buckets_inner}
                buckets_out.append(bucket_out)
                idx += 1
                bucket = buckets[idx]
                bucket_out = self._build_bucket_out(
                    bucket, label_map, key_prefix, filter_values)
                buckets_inner = []

        if buckets_inner:
            bucket_out["inner"] = {'buckets': buckets_inner}

        buckets_out.append(bucket_out)

        return idx, buckets_out

    def get_labelled_values(self, data, filter_values, bucket_label=True,
                            key_prefix=None):
        """Get a labelled version of a bucket."""
        out = []
        # We get the labels first, so that we can efficiently query a resource
        # for all keys in one go, vs querying one by one if needed.
        label_buckets = self._build_nested_buckets(data.buckets)
        label_map = self.get_label_mapping(label_buckets)

        assert len(label_buckets) == len(label_map)

        if label_buckets:
            _, out = self._build_bucket_list(
                label_buckets, label_map, key_prefix, filter_values
            )
        ret_val = {'buckets': out}

        if bucket_label:
            ret_val['label'] = str(self._label)
        return ret_val
