using MovieLibrary.Application.Queries.Movies.ListMovies;
using MovieLibrary.Application.Responses.Movies;

namespace MovieLibrary.Presentation.Controllers;

/// <summary>
/// Public API controller to handle requests related to movies.
/// </summary>
[ApiController, ApiVersion("1"), Produces(contentType: ContentTypes.Json)]
[Route(template: "api/[controller]/v{version:ApiVersion}")]
public class MoviesController(IMediator mediator) : ApiResultController
{
    /// <summary>
    /// Lists movies. Filtering and pagination may be applied.
    /// </summary>
    /// <param name="query">The object that encapsulates filter, pagination and sorting properties of the query.</param>
    /// <param name="cancellationToken">A token that propagates notification that this request should be canceled.</param>
    /// <response code="200">Returns a list containing the movies. The list may be empty if any of the query params do not match.</response>
    /// <response code="401">Either you are not authenticated or you do not have access level for this resource.</response>
    [Authorize(Roles = AuthorizationRoles.AdminUser)]
    [HttpGet(Name = "List movies")]
    [ProducesResponseType(statusCode: StatusCodes.Status200OK, type: typeof(DefaultMovieResponse[]))]
    public async Task<IActionResult> GetMoviesAsync([FromQuery] ListMoviesQuery query,
        CancellationToken cancellationToken = default)
    {
        return BuildStatusCodeObject(await mediator.Send(query, cancellationToken));
    }
}