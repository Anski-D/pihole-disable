def _clean_period_value(period: int | str) -> int:
    return max(0, int(period))


def _check_client(_client: str) -> bool:
    if len(_client) > 4*3 + 3:
        return False

    if len(client_parts := _client.split(".")) != 4:
        return False

    if any(not part.isdigit() for part in client_parts):
        return False

    if any(not (0 <= int(part) < 256) for part in client_parts):
        return False

    return True
