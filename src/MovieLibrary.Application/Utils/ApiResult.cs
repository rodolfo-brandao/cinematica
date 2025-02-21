namespace MovieLibrary.Application.Utils;

/// <summary>
/// Basic wrapper responsible for encapsulating success or
/// failure information about actions performed by the handlers.
/// </summary>
/// <param name="statusCode">The appropriate HTTP status code for the result of the action performed.</param>
/// <typeparam name="TResponse">The type of response based on the result of the action performed.
/// If the return type of the operation is <see langword="void"/>, <see cref="Unit"/> must be used.</typeparam>
public class ApiResult<TResponse>(int statusCode = (int)HttpStatusCode.OK)
{
    public int StatusCode { get; set; } = statusCode;
    public TResponse Response { get; set; } = default;
    public string ErrorMessage { get; set; } = null;
}
