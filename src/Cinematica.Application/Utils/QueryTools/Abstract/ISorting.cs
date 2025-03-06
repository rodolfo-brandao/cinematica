namespace Cinematica.Application.Utils.QueryTools.Abstract;

/// <summary>
/// Exposes basic properties for sorting in queries.
/// </summary>
public interface ISorting
{
    /// <summary>
    /// The direction to sort the results by. Can be one of: "asc", "desc".
    /// Default is "asc".
    /// </summary>
    public string Direction { get; set; }

    /// <summary>
    /// Indicates the name of the property that will be used as a
    /// comparator for sorting.
    /// </summary>
    public string SortBy { get; set; }
}