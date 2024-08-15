namespace MovieLibrary.Application.Responses.Movies;

public class DefaultMovieResponse
{
    public Guid Id { get; init; }
    public string Name { get; init; }
    public string OriginalName { get; init; }
    public string Year { get; init; }
    public string Runtime { get; init; }
    public string Country { get; init; }
    public string Genres { get; init; }
}
