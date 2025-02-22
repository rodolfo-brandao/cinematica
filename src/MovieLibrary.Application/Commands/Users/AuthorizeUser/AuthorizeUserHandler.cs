using MovieLibrary.Application.Responses.Users;
using MovieLibrary.Application.Utils;
using MovieLibrary.Core.Contracts.Repositories;
using MovieLibrary.Core.Contracts.Services;
using MovieLibrary.Core.Models.Nulls;

namespace MovieLibrary.Application.Commands.Users.AuthorizeUser;

public class AuthorizeUserHandler(IUserRepository userRepository, ISecurityService securityService) : IRequestHandler<AuthorizeUserCommand, ApiResult<AuthorizedUserResponse>>
{
    public async Task<ApiResult<AuthorizedUserResponse>> Handle(AuthorizeUserCommand request, CancellationToken cancellationToken)
    {
        var apiResult = new ApiResult<AuthorizedUserResponse>();

        var user = await userRepository.GetByUsernameAsync(request.Username);

        if (user is NullUser)
        {
            apiResult.StatusCode = (int)HttpStatusCode.BadRequest;
            apiResult.ErrorMessage = $"No user with username '{request.Username}' was found.";
        }
        else if (!securityService.ValidatePassword(request.Password, user.Password, user.PasswordSalt))
        {
            apiResult.StatusCode = (int)HttpStatusCode.BadRequest;
            apiResult.ErrorMessage = "Wrong password.";
        }
        else
        {
            var expirationTime = new TimeOnly(hour: 2, minute: 0);
            var token = securityService.CreateJsonWebToken(user, expirationTime);
            apiResult.Response = new AuthorizedUserResponse
            {
                Username = user.Username,
                Token = token,
                Type = "Bearer",
                ExpiresOn = $"{DateTime.UtcNow.AddHours(expirationTime.Hour):yyyy-MM-dd HH:mm:ss} UTC"
            };
        }

        return await Task.FromResult(apiResult);
    }
}
