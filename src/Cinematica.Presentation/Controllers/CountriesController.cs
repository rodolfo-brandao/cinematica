using Cinematica.Application.Commands.Countries.CreateCountry;
using Cinematica.Application.Commands.Countries.DeleteCountry;
using Cinematica.Application.Queries.Countries.ListCountries;
using Cinematica.Application.Responses.Countries;

namespace Cinematica.Presentation.Controllers;

/// <summary>
/// Public API controller to handle requests related to countries.
/// </summary>
[ApiController, ApiVersion("1"), Produces(contentType: ContentTypes.Json)]
[Route(template: "api/[controller]/v{version:ApiVersion}")]
public class CountriesController(IMediator mediator) : ApiResultHandlerController
{
    /// <summary>
    /// Lists countries. Filtrering and pagination may be applied.
    /// </summary>
    /// <param name="query">The object that encapsulates filter, pagination and sorting properties of the query.</param>
    /// <param name="cancellationToken">A token that propagates notification that this request should be canceled.</param>
    /// <response code="200">Returns a list containing the countries. The list may be empty if any of the query params do not match.</response>
    /// <response code="401">Either you are not authenticated or don't have access level for this resource.</response>
    [Authorize(Roles = AuthorizationRoles.AdminUser)]
    [HttpGet(Name = "list-countries")]
    [ProducesResponseType(statusCode: StatusCodes.Status200OK, type: typeof(DefaultCountryResponse[]))]
    public async Task<IActionResult> GetCountriesAsync([FromQuery] ListCountriesQuery query,
        CancellationToken cancellationToken)
    {
        return BuildStatusCodeObject(await mediator.Send(query, cancellationToken));
    }

    /// <summary>
    /// Creates a new country.
    /// </summary>
    /// <param name="command">The payload containing all data needed to create a new country.</param>
    /// <param name="cancellationToken">A token that propagates notification that this request should be canceled.</param>
    /// <response code="201">Returns essential information about the newly created user.</response>
    /// <response code="400">There was an error when trying to validate the request payload.</response>
    /// <response code="401">Either you are not authenticated or don't have access level for this resource.</response>
    [HttpPost(Name = "create-country")]
    [Authorize(Roles = AuthorizationRoles.Admin)]
    [ProducesResponseType(statusCode: StatusCodes.Status201Created, type: typeof(CreatedCountryResponse))]
    public async Task<IActionResult> CreateCountryAsync([FromBody] CreateCountryCommand command, CancellationToken cancellationToken)
    {
        return BuildStatusCodeObject(await mediator.Send(command, cancellationToken));
    }

    /// <summary>
    /// Performs a physical deletion on a single country.
    /// </summary>
    /// <param name="id">The country's unique identifier.</param>
    /// <param name="cancellationToken">A token that propagates notification that this request should be canceled.</param>
    /// <response code="204">Country deleted successfully.</response>
    /// <response code="401">Either you are not authenticated or don't have access level for this resource.</response>
    /// <response code="404">Country not found.</response>
    [Authorize(Roles = AuthorizationRoles.Admin)]
    [HttpDelete(template: "{id:guid}", Name = "delete-country")]
    public async Task<IActionResult> DeleteCountryAsync([FromRoute] Guid id, CancellationToken cancellationToken)
    {
        var command = new DeleteCountryCommand(id);
        return BuildStatusCodeObject(await mediator.Send(command, cancellationToken));
    }
}
