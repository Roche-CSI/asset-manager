from deepdiff import Delta, DeepDiff


def compute_dict_patch(prev_dict: dict, curr_dict: dict) -> str:
    """Computes the diff patch between two assets
    Parameters:
        prev_assets dict of previous assets against which the diff will be calculated
        curr_assets dict of current assets
    Returns:
        serialized representation of the delta object
    """
    ddiff = DeepDiff(prev_dict, curr_dict)
    delta = Delta(diff=ddiff)
    return delta.dumps().hex()
    # return ddiff.to_json_pickle()


def apply_dict_patch(prev_dict: dict, patch: str) -> dict:
    """Applies patch to an existing text and returns the updated text
    Parameters:
        prev_assets dict of assets
        patch serialized representation of delta object
    Returns:
        resultant assets dict
    """
    delta = Delta(bytes.fromhex(patch))
    # delta = Delta(bytes.fromhex(patch))
    return prev_dict + delta