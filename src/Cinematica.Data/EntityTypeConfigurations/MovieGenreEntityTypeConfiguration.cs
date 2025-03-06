using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Cinematica.Core.Models;

namespace Cinematica.Data.EntityTypeConfigurations;

public class MovieGenreEntityTypeConfiguration : IEntityTypeConfiguration<MovieGenre>
{
    public void Configure(EntityTypeBuilder<MovieGenre> builder)
    {
        builder.ToTable("movie_genre");

        builder.HasKey(movieGenre => new
        {
            movieGenre.MovieId,
            movieGenre.GenreId
        });

        builder.Property(movieGenre => movieGenre.MovieId)
            .HasColumnName("movie_id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(movieGenre => movieGenre.GenreId)
            .HasColumnName("genre_id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        #region Navigation Properties Cardinality

        builder.HasOne(movieGenre => movieGenre.Movie)
            .WithMany(movie => movie.MovieGenres)
            .HasForeignKey(movieGenre => movieGenre.MovieId)
            .HasConstraintName("FK_movie_movie_genre")
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(movieGenre => movieGenre.Genre)
            .WithMany(genre => genre.MovieGenres)
            .HasForeignKey(movieGenre => movieGenre.GenreId)
            .HasConstraintName("FK_genre_movie_genre")
            .OnDelete(DeleteBehavior.Restrict);

        #endregion
    }
}