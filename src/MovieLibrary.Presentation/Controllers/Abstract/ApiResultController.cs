using MovieLibrary.Application.Utils;

namespace MovieLibrary.Presentation.Controllers.Abstract;

/// <summary>
/// Abstract controller to manage status code objects
/// according to commands/queries performed by the application.
/// </summary>
public abstract class ApiResultController : ControllerBase
{
    /// <summary>
    /// Builds the proper status code object based on the <see cref="ApiResult{TResponse}"/>.
    /// </summary>
    /// <typeparam name="TResponse">The type of the response.</typeparam>
    protected IActionResult BuildResponse<TResponse>(ApiResult<TResponse> apiResult)
    {
        return apiResult.StatusCode switch
        {
            StatusCodes.Status200OK => Ok(apiResult.Response),
            StatusCodes.Status201Created => CreatedAtAction(actionName: default, apiResult.Response),
            StatusCodes.Status204NoContent => NoContent(),
            StatusCodes.Status400BadRequest => BadRequest(apiResult.ErrorMessage),
            StatusCodes.Status404NotFound => NotFound(),
            _ => Problem(statusCode: StatusCodes.Status500InternalServerError, detail: apiResult.ErrorMessage),
        };
    }
}
