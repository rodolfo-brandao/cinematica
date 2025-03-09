using Cinematica.Application.Utils;

namespace Cinematica.Application.Commands.Users.DeleteUser;

public class DeleteUserCommand(Guid id) : IRequest<ApiResult<Unit>>
{
    public Guid Id { get; init; } = id;
}