from src.utils import canonicalize_entity, slugify


def test_canonicalize_entity_removes_extra_spaces():
    assert canonicalize_entity("  ChatGPT   para SEO!! ") == "chatgpt para seo"


def test_slugify_entity():
    assert slugify("IA generativa para SEO") == "ia-generativa-para-seo"
