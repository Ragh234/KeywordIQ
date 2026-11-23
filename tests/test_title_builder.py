from amazon_keyword_tool.analysis.title_builder import build_title

TOP = ["bluetooth", "noise cancelling", "wireless earbuds", "mic", "fast charging", "playtime"]
GAPS = ["ipx5 water resistant", "usb c"]


def _words(title: str) -> list[str]:
    return title.lower().split()


def test_title_starts_with_title_cased_search_keyword():
    result = build_title("wireless earbuds", TOP, GAPS)

    assert result["title"].startswith("Wireless Earbuds")


def test_title_never_exceeds_max_length():
    many = [f"feature{i} extra{i}" for i in range(80)]

    for limit in (40, 80, 200):
        result = build_title("wireless earbuds", many, many, max_len=limit)
        assert len(result["title"]) <= limit
        assert result["length"] == len(result["title"])
        assert result["max_length"] == limit


def test_limit_shown_to_the_user_is_amazons_200_characters():
    result = build_title("wireless earbuds", ["bluetooth"], [])

    assert result["max_length"] == 200


def test_title_has_no_repeated_words():
    result = build_title("wireless earbuds", TOP, GAPS)
    words = _words(result["title"])

    assert len(words) == len(set(words))


def test_keyword_already_covered_by_title_is_skipped():
    result = build_title("wireless earbuds", ["wireless earbuds", "earbuds"], [])

    assert result["title"] == "Wireless Earbuds"
    assert result["keywords_used"] == []


def test_partially_overlapping_phrase_only_adds_the_new_words():
    result = build_title("wireless earbuds", ["earbuds mic"], [])

    assert result["title"] == "Wireless Earbuds Mic"
    assert result["keywords_used"] == ["earbuds mic"]


def test_top_and_gap_keywords_are_both_used():
    result = build_title("wireless earbuds", TOP, GAPS)
    title = result["title"].lower()

    assert "bluetooth" in title            # from top keywords
    assert "ipx5 water resistant" in title  # from competitor gaps


def test_gap_keywords_are_not_crowded_out_by_top_keywords():
    top = [f"feature{i}" for i in range(50)]

    result = build_title("wireless earbuds", top, ["ipx5"], max_len=60)

    assert "Ipx5" in result["title"]


def test_keyword_that_does_not_fit_is_skipped_but_shorter_ones_still_added():
    result = build_title(
        "earbuds", ["averyveryverylongkeywordthatwillnotfit", "mic"], [], max_len=20
    )

    assert result["title"] == "Earbuds Mic"


def test_no_keywords_returns_just_the_search_keyword():
    result = build_title("gaming mouse", [], [])

    assert result["title"] == "Gaming Mouse"
    assert result["keywords_used"] == []
    assert result["length"] == len("Gaming Mouse")


def test_keywords_used_lists_what_was_added():
    result = build_title("wireless earbuds", ["bluetooth", "mic"], [])

    assert result["keywords_used"] == ["bluetooth", "mic"]


def test_overlong_search_keyword_is_cut_at_a_word_boundary():
    result = build_title("alpha beta gamma delta", [], [], max_len=12)

    assert result["title"] == "Alpha Beta"
    assert len(result["title"]) <= 12


def test_empty_search_keyword_gives_empty_title():
    result = build_title("   ", TOP, GAPS)

    assert result["title"] == ""
    assert result["length"] == 0


# ── Regression: real extractor output has overlapping n-gram fragments ───────
# The extractor returns "water", "resistant", "water resistant", "ipx5 water"
# ... for the same phrase. Stitching fragments together used to scramble the
# word order ("Water Cancelling Resistant").

REAL_TOP = [
    "bluetooth", "wireless earbuds", "earbuds", "wireless", "mic", "touch control",
    "control", "touch", "usb", "water", "resistant touch", "ipx5", "ipx5 water",
    "touch control noise", "water resistant", "noise", "resistant", "control noise",
    "resistant touch control", "earbuds ipx5",
]
REAL_GAPS = [
    "ipx5", "resistant", "ipx5 water", "resistant touch", "earbuds ipx5", "water",
    "noise cancelling", "cancelling", "noise", "control noise", "water resistant",
    "cancelling usb", "usb bluetooth",
]


def test_every_keyword_used_appears_intact_and_in_order_in_the_title():
    result = build_title("wireless earbuds", REAL_TOP, REAL_GAPS)
    title = result["title"].lower()

    assert result["keywords_used"], "expected some keywords to be added"
    for keyword in result["keywords_used"]:
        assert keyword in title, f"{keyword!r} was split up in {result['title']!r}"


def test_overlapping_fragments_are_merged_in_reading_order():
    result = build_title("earbuds", ["ipx5 water", "water resistant"], [])

    assert result["title"] == "Earbuds Ipx5 Water Resistant"


def test_fragments_of_an_added_phrase_are_not_added_again():
    result = build_title("earbuds", ["ipx5", "water", "ipx5 water"], [])

    assert result["title"] == "Earbuds Ipx5 Water"
    assert result["keywords_used"] == ["ipx5 water"]


def test_continuations_are_chained_right_after_the_phrase_they_extend():
    # "mic" is higher priority than "water resistant", but "water resistant"
    # continues "ipx5 water", so it must follow it directly instead of being
    # separated by unrelated keywords.
    result = build_title("earbuds", ["ipx5 water", "mic", "water resistant"], [])

    assert result["title"] == "Earbuds Ipx5 Water Resistant Mic"


def test_chain_of_overlapping_phrases_reads_like_the_original_title():
    result = build_title("wireless earbuds", REAL_TOP, REAL_GAPS)

    assert "ipx5 water resistant touch control" in result["title"].lower()


def test_phrase_is_not_merged_if_that_would_repeat_a_word():
    # "water resistant water" would repeat "water" if merged naively.
    result = build_title("earbuds water", ["water resistant water"], [])

    words = result["title"].lower().split()
    assert len(words) == len(set(words))


# Exact keyword lists the live API returned for the failing case: the title
# came out as "... Mic Control Noise Cancelling Usb Bluetooth Ipx5 Water
# Resistant Touch", with "Touch" stranded away from "Control Noise Cancelling".
LIVE_TOP = [
    "bluetooth", "earbuds", "wireless earbuds", "wireless", "mic", "touch control", "control",
    "touch", "usb", "wireless earbuds ipx5", "earbuds ipx5 water", "control noise cancelling",
    "earbuds ipx5", "ipx5 water", "resistant", "water", "touch control noise",
    "ipx5 water resistant", "noise cancelling", "water resistant touch",
]
LIVE_GAPS = [
    "earbuds ipx5", "resistant touch", "resistant", "ipx5 water", "noise cancelling", "ipx5",
    "water resistant", "cancelling", "water", "control noise", "noise", "cancelling usb",
    "usb bluetooth",
]


def test_overlapping_trigrams_are_merged_into_one_reading_order_chain():
    result = build_title("wireless earbuds", LIVE_TOP, LIVE_GAPS)

    assert "ipx5 water resistant touch control noise cancelling" in result["title"].lower()


def test_live_case_title_has_no_repeated_words_and_every_keyword_intact():
    result = build_title("wireless earbuds", LIVE_TOP, LIVE_GAPS)
    words = result["title"].lower().split()

    assert len(words) == len(set(words))
    for keyword in result["keywords_used"]:
        assert keyword in result["title"].lower()


def test_chain_too_long_to_fit_falls_back_to_its_shorter_phrases():
    # The merged chain "aa bb cc dd ee" is 14 chars; only "aa bb" (5) fits.
    result = build_title("x", ["aa bb", "bb cc", "cc dd", "dd ee"], [], max_len=8)

    assert result["title"] == "X Aa Bb"


# ── Readable length: aim for ~120 characters, never exceed Amazon's 200 ──────

MANY = [f"feature{i} extra{i}" for i in range(80)]


def test_default_title_aims_for_a_readable_length_not_the_hard_limit():
    result = build_title("wireless earbuds", MANY, [])

    assert result["max_length"] == 200           # the limit shown to the seller
    assert 100 < len(result["title"]) <= 120     # but the title stops at the target


def test_target_length_can_be_raised_up_to_the_hard_limit():
    result = build_title("wireless earbuds", MANY, [], target_len=200)

    assert 150 < len(result["title"]) <= 200


def test_target_length_never_exceeds_the_hard_limit():
    result = build_title("wireless earbuds", MANY, [], max_len=60, target_len=200)

    assert len(result["title"]) <= 60


def test_multi_word_phrases_are_added_before_single_words():
    # Only room for one of them: the 3-word phrase should win over lone words.
    result = build_title("earbuds", ["mic", "usb", "ipx5 water resistant", "led"], [], target_len=30)

    assert result["title"] == "Earbuds Ipx5 Water Resistant"


def test_single_words_still_fill_the_remaining_room():
    result = build_title("earbuds", ["mic", "ipx5 water resistant"], [], target_len=60)

    assert result["title"] == "Earbuds Ipx5 Water Resistant Mic"


# Real keyword lists from a live amazon.in "wireless earbuds" scrape. The old
# builder produced a 133-character title ending in stray words ("... Noise
# Type Dual"); phrases should now come first and the title should stay short.
EARBUDS_TOP = [
    "wireless", "bluetooth", "ear", "earbuds", "tws", "charging", "wireless earbuds",
    "fast charging", "fast", "mic", "touch", "drivers", "playtime", "earphones", "buds",
    "touch control", "control", "noise", "type", "dual",
]
EARBUDS_GAPS = ["earbuds tws", "headphones", "tws ear", "led", "40h"]


def test_real_earbuds_title_is_short_and_puts_phrases_before_single_words():
    result = build_title("wireless earbuds", EARBUDS_TOP, EARBUDS_GAPS)
    title = result["title"].lower()

    assert result["length"] <= 120
    assert title.index("fast charging") < title.index("bluetooth")
    assert title.index("touch control") < title.index("bluetooth")
    for stray in ("noise", "type", "dual"):
        assert stray not in title.split(), f"stray word {stray!r} should not be in {result['title']!r}"
    for keyword in result["keywords_used"]:
        assert keyword in title
