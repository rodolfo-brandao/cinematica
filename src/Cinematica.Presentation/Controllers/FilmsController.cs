using Cinematica.Application.Queries.Films.ListFilms;
using Cinematica.Application.Responses.Films;

namespace Cinematica.Presentation.Controllers;

/// <summary>
/// Public API controller to handle requests related to films.
/// </summary>
[ApiController, ApiVersion("1"), Produces(contentType: ContentTypes.Json)]
[Route(template: "api/[controller]/v{version:ApiVersion}")]
public class FilmsController(IMediator mediator) : ApiResultHandlerController
{
    /// <summary>
    /// Lists films. Filtering and pagination may be applied.
    /// </summary>
    /// <param name="query">The object that encapsulates filter, pagination and sorting properties of the query.</param>
    /// <param name="cancellationToken">A token that propagates notification that this request should be canceled.</param>
    /// <response code="200">
    /// Returns a list containing the films.
    /// The list may be empty if any of the query params do not match.
    /// </response>
    /// <response code="401">Either you are not authenticated or don't have access level for this resource.</response>
    [Authorize(Roles = AuthorizationRoles.AdminUser)]
    [HttpGet(Name = "list-films")]
    [ProducesResponseType(statusCode: StatusCodes.Status200OK, type: typeof(DefaultFilmResponse[]))]
    public async Task<IActionResult> GetFilmsAsync([FromQuery] ListFilmsQuery query,
        CancellationToken cancellationToken = default)
    {
        return BuildStatusCodeObject(await mediator.Send(query, cancellationToken));
    }
}
