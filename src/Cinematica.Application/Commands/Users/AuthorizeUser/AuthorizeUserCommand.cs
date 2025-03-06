using Cinematica.Application.Responses.Users;
using Cinematica.Application.Utils;

namespace Cinematica.Application.Commands.Users.AuthorizeUser;

public class AuthorizeUserCommand : IRequest<ApiResult<AuthorizedUserResponse>>
{
    public string Username { get; init; }
    public string Password { get; init; }
}
