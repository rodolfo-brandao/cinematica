namespace Cinematica.Application.Responses.Users;

public class CreatedUserResponse
{
    public Guid Id { get; init; }
    public string Username { get; init; }
    public string Role { get; init; }
    public string CreatedOn { get; init; }
}
