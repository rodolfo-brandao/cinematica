namespace Cinematica.Application.Responses.Users;

public class AuthorizedUserResponse
{
    public string Username { get; init; }
    public string Token { get; init; }
    public string Type { get; init; }
    public string ExpiresOn { get; init; }
}
