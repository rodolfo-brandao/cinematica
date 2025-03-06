using Cinematica.Application.Responses.Users;
using Cinematica.Application.Utils;
using Cinematica.Application.Utils.Constants;
using Cinematica.Core.Contracts.Factories;
using Cinematica.Core.Contracts.Repositories;
using Cinematica.Core.Contracts.Services;
using Cinematica.Core.Contracts.Units;

namespace Cinematica.Application.Commands.Users.CreateUser;

public class CreateUserHandler(
    IUserRepository userRepository,
    ISecurityService securityService,
    IUnitOfWork unitOfWork,
    IModelFactory modelFactory)
    : IRequestHandler<CreateUserCommand, ApiResult<CreatedUserResponse>>
{
    public async Task<ApiResult<CreatedUserResponse>> Handle(CreateUserCommand request,
        CancellationToken cancellationToken)
    {
        var apiResult = new ApiResult<CreatedUserResponse>();
        var validationResult = await new CreateUserCommandValidator(userRepository)
            .ValidateAsync(request, cancellationToken);

        if (validationResult.IsValid)
        {
            var (password, passwordSalt) = securityService.CreatePasswordHash(request.Password);
            var user = modelFactory.CreateUser(
                username: request.Username.ToLower(),
                email: request.Email.ToLower(),
                password: password,
                passwordSalt: passwordSalt,
                role: request.IsAdmin ? AuthorizationRoles.Admin : AuthorizationRoles.User);

            var createdUser = await userRepository.InsertAsync(user);
            _ = await unitOfWork.SaveChangesAsync();
            apiResult.Response = new CreatedUserResponse
            {
                Id = createdUser.Id,
                Username = createdUser.Username,
                Role = createdUser.Role,
                CreatedOn = createdUser.CreatedOn.ToLongDateString()
            };
        }
        else
        {
            apiResult.StatusCode = (int)HttpStatusCode.BadRequest;
            apiResult.ErrorMessage = validationResult.Errors.First().ErrorMessage;
        }

        return apiResult;
    }
}