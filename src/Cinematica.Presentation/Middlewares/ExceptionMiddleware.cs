using System.Diagnostics.CodeAnalysis;
using System.Text.Json;
using Cinematica.Application.Utils.Constants;

namespace Cinematica.Presentation.Middlewares;

/// <summary>
/// Middleware to handle unexpected/generic exceptions thrown by the application.
/// </summary>
[ExcludeFromCodeCoverage]
internal class ExceptionMiddleware(RequestDelegate requestDelegate)
{
    /// <summary>
    /// Handles all requests processed by the Application layer for any unexpected backend behavior.
    /// </summary>
    /// <param name="httpContext">The context of which the HTTP request to be processed belongs.</param>
    /// <returns>A response with details of the exception thrown.</returns>
    public async Task InvokeAsync(HttpContext httpContext)
    {
        try
        {
            await requestDelegate(httpContext);
        }
        catch (Exception e)
        {
            await HandleExceptionAsync(httpContext, e);
        }
    }

    #region Private Methods

    private static Task HandleExceptionAsync(HttpContext httpContext, Exception exception)
    {
        var responseBody = JsonSerializer.Serialize(new
        {
            error = exception.Message
        });

        httpContext.Response.ContentType = ContentTypes.Json;
        httpContext.Response.StatusCode = StatusCodes.Status500InternalServerError;

        return httpContext.Response.WriteAsync(responseBody);
    }

    #endregion
}
