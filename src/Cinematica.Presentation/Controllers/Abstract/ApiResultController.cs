using Cinematica.Application.Utils;

namespace Cinematica.Presentation.Controllers.Abstract;

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
    /// <param name="apiResult">The respective API result object containing the success or failure response.</param>
    /// <param name="actionName">The name of the action to use for generating the redirect URL for when the response status code is '201 Created'.</param>
    protected IActionResult BuildStatusCodeObject<TResponse>(ApiResult<TResponse> apiResult, string actionName = null)
    {
        return apiResult.StatusCode switch
        {
            StatusCodes.Status200OK => Ok(apiResult.Response),
            StatusCodes.Status201Created => CreatedAtAction(actionName: actionName, apiResult.Response),
            StatusCodes.Status204NoContent => NoContent(),
            StatusCodes.Status400BadRequest => BadRequest(apiResult.ErrorMessage),
            StatusCodes.Status404NotFound => NotFound(value: apiResult.ErrorMessage),
            _ => Problem(statusCode: StatusCodes.Status500InternalServerError, detail: apiResult.ErrorMessage),
        };
    }
}