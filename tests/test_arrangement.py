from arrangement import Arrangement, Placement, to_solution_dict


def test_a_new_arrangement_has_no_placements():
    arrangement = Arrangement()

    assert arrangement.placement_at(0, 0) is None
    assert not arrangement.is_complete()


def test_placement_at_returns_none_outside_the_grid():
    arrangement = Arrangement()

    assert arrangement.placement_at(-1, 0) is None
    assert arrangement.placement_at(0, 3) is None
    assert arrangement.placement_at(4, 0) is None


def test_with_placement_records_a_placement_without_changing_the_original(make_card):
    empty = Arrangement()
    placement = Placement(make_card(7), 90)

    filled = empty.with_placement(2, 1, placement)

    assert filled.placement_at(2, 1) == placement
    assert empty.placement_at(2, 1) is None


def test_an_arrangement_is_complete_once_every_cell_is_filled(make_card):
    arrangement = Arrangement()
    for y in range(3):
        for x in range(4):
            arrangement = arrangement.with_placement(x, y, Placement(make_card(), 0))

    assert arrangement.is_complete()


def test_to_solution_dict_keys_cells_by_coordinate_from_the_top_left(make_card):
    arrangement = Arrangement().with_placement(0, 0, Placement(make_card(3), 0))
    arrangement = arrangement.with_placement(3, 2, Placement(make_card(11), 270))

    solution = to_solution_dict(arrangement)

    assert solution["0,0"] == {"card": 3, "orientation": 0}
    assert solution["3,2"] == {"card": 11, "orientation": 270}
