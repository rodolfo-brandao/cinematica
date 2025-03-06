using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Cinematica.Core.Models;

namespace Cinematica.Data.EntityTypeConfigurations;

public class FilmGenreEntityTypeConfiguration : IEntityTypeConfiguration<FilmGenre>
{
    public void Configure(EntityTypeBuilder<FilmGenre> builder)
    {
        builder.ToTable("film_genre");

        builder.HasKey(filmGenre => new
        {
            filmGenre.FilmId,
            filmGenre.GenreId
        });

        builder.Property(filmGenre => filmGenre.FilmId)
            .HasColumnName("film_id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(filmGenre => filmGenre.GenreId)
            .HasColumnName("genre_id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        #region Navigation Properties Cardinality

        builder.HasOne(filmGenre => filmGenre.Film)
            .WithMany(movie => movie.FilmGenres)
            .HasForeignKey(filmGenre => filmGenre.FilmId)
            .HasConstraintName("FK_film_film_genre")
            .OnDelete(DeleteBehavior.Restrict);

        builder.HasOne(filmGenre => filmGenre.Genre)
            .WithMany(genre => genre.FilmGenres)
            .HasForeignKey(filmGenre => filmGenre.GenreId)
            .HasConstraintName("FK_genre_film_genre")
            .OnDelete(DeleteBehavior.Restrict);

        #endregion
    }
}