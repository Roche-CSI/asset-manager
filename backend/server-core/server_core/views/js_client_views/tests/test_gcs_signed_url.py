from views.js_client_views.gcs_signed_url_view import signed_url_for_content


def test_signed_url_for_content():
    data = {
        "created_at": "2022/06/21 13-40-19 -0700",
        "created_by": "zhul76",
        "hash": "md5_placeholder_id_000==",
        "id": "gs:proxy_md5_0aa00000000aa0000000aa==",
        "meta": {
            "proxy": True,
            "src": "gs://example_bucket/dl-training/additional_annotations/plot_median_accuracy_read_length_comparison-post_qc.png",
            "type": "gcs"
        },
        "mime_type": "image/png",
        "size": 266575
    }
    class_id = "b45264a8-4fcc-4671-bf50-8bb8ceb44413"
    url = signed_url_for_content(content_data=data, class_id=class_id)
    file_name = "plot_median_accuracy_read_length_comparison-post_qc.png"
    assert file_name in url

    # non-proxy content
    data = {
        "created_at": "2022/06/21 13-40-19 -0700",
        "created_by": "user1",
        "hash": "md5_placeholder_id_001==",
        "id": "gs:proxy_md5_0aa00000000aa0000000aa==",
        "meta": {
            "src": "gs://example_bucket/dl-training/additional_annotations/plot_median_accuracy_read_length_comparison-post_qc.png",
            "type": "gcs"
        },
        "mime_type": "image/png",
        "size": 266575
    }
    url = signed_url_for_content(content_data=data, class_id="00000000-0000-0000-0000-000000000001")
    # content = ContentFactory().de_serialize(asset=None, data=data)
    assert class_id in url
