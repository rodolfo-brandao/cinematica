using Cinematica.Application.Commands.Users.AuthorizeUser;
using Cinematica.Application.Commands.Users.CreateUser;
using Cinematica.Application.Commands.Users.DeleteUser;
using Cinematica.Application.Responses.Users;

namespace Cinematica.Presentation.Controllers;

/// <summary>
/// Public API controller to handle requests related to users.
/// </summary>
[ApiController, ApiVersion("1"), Produces(contentType: ContentTypes.Json)]
[Route(template: "api/[controller]/v{version:ApiVersion}")]
public class UsersController(IMediator mediator) : ApiResultController
{
    /// <summary>
    /// Creates a new user.
    /// </summary>
    /// <param name="command">The payload containing all data needed to create a new user.</param>
    /// <param name="cancellationToken">A token that propagates notification that this request should be canceled.</param>
    /// <response code="201">Returns essential information about the newly created user.</response>
    /// <response code="400">There was an error when trying to validate the request payload.</response>
    [AllowAnonymous]
    [HttpPost("new", Name = "create-user")]
    [ProducesResponseType(statusCode: StatusCodes.Status201Created, type: typeof(CreatedUserResponse))]
    public async Task<IActionResult> CreateUserAsync([FromBody] CreateUserCommand command,
        CancellationToken cancellationToken)
    {
        return BuildStatusCodeObject(await mediator.Send(command, cancellationToken));
    }

    /// <summary>
    /// Performs a physical deletion on a single user.
    /// </summary>
    /// <param name="id">The user's unique identifier.</param>
    /// <param name="cancellationToken">A token that propagates notification that this request should be canceled.</param>
    /// <response code="204">User deleted successfully.</response>
    /// <response code="401">Either you are not authenticated or you don't have access level for this resource.</response>
    /// <response code="404">The user was not found.</response>
    [Authorize(Roles = AuthorizationRoles.AdminUser)]
    [HttpDelete("{id:guid}", Name = "delete-user")]
    public async Task<IActionResult> DeleteUserAsync([FromRoute] Guid id, CancellationToken cancellationToken)
    {
        var command = new DeleteUserCommand(id);
        return BuildStatusCodeObject(await mediator.Send(command, cancellationToken));
    }

    /// <summary>
    /// Authorizes an existing user by issuing a JSON Web Token (JWT).
    /// </summary>
    /// <param name="command">The payload containing all data needed to validate a user and issue a JSON Web Token (JWT).</param>
    /// <param name="cancellationToken">A token that propagates notification that this request should be canceled.</param>
    /// <response code="200">Returns the newly issued JSON Web Token (JWT) along with some essential information.</response>
    /// <response code="400">There was an error when trying to validate the request payload.</response>
    [AllowAnonymous]
    [HttpPost("token", Name = "authorize-user")]
    [ProducesResponseType(statusCode: StatusCodes.Status200OK, type: typeof(AuthorizedUserResponse))]
    public async Task<IActionResult> IssueJsonWebTokenAsync([FromBody] AuthorizeUserCommand command,
        CancellationToken cancellationToken)
    {
        return BuildStatusCodeObject(await mediator.Send(command, cancellationToken));
    }
}