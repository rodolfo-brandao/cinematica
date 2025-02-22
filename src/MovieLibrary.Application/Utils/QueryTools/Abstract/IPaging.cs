namespace MovieLibrary.Application.Utils.QueryTools.Abstract;

/// <summary>
/// Exposes basic properties for paging in queries.
/// </summary>
public interface IPaging
{
    /// <summary>
    /// Represents the current page number.
    /// </summary>
    public int Page { get; set; }

    /// <summary>
    /// Indicates the number of items to be listed per page.
    /// </summary>
    public int PageSize { get; set; }
}