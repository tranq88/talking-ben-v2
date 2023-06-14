def find_user(server_accs: dict[str, dict], discord_id: int) -> str:
    """
    Search <server_accs> and return the username
    associated with <discord_id>.
    """
    for username in server_accs:
        if server_accs[username]['discord_id'] == discord_id:
            return username

    raise LookupError
