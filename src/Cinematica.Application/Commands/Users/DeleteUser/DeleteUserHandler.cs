using Cinematica.Application.Utils;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Contracts.Units;
using Cinematica.Core.Models.Nulls;
using Microsoft.AspNetCore.Http;

namespace Cinematica.Application.Commands.Users.DeleteUser;

public class DeleteUserHandler(IUserRepository userRepository, IUnitOfWork unitOfWork)
    : IRequestHandler<DeleteUserCommand, ApiResult<Unit>>
{
    public async Task<ApiResult<Unit>> Handle(DeleteUserCommand request, CancellationToken cancellationToken)
    {
        var apiResult = new ApiResult<Unit>(statusCode: StatusCodes.Status204NoContent);
        var user = await userRepository.GetByKeyAsync(request.Id) ?? new NullUser();

        if (user is NullUser)
        {
            apiResult.StatusCode = StatusCodes.Status404NotFound;
            apiResult.ErrorMessage = "User not found.";
        }
        else
        {
            _ = userRepository.Remove(user);
            _ = await unitOfWork.SaveChangesAsync();
        }

        return apiResult;
    }
}