using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using MovieLibrary.Core.Models;

namespace MovieLibrary.Data.EntityTypeConfigurations;

public class CountryEntityTypeConfiguration : IEntityTypeConfiguration<Country>
{
    public void Configure(EntityTypeBuilder<Country> builder)
    {
        builder.ToTable("country");

        builder.HasKey(country => country.Id);

        builder.Property(country => country.Id)
            .HasColumnName("id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(country => country.Name)
            .HasColumnName("name")
            .HasColumnType("VARCHAR(255)")
            .IsRequired();

        builder.Property(country => country.IsoAlpha3Code)
            .HasColumnName("iso_alpha3_code")
            .HasColumnType("CHAR(3)")
            .IsRequired();

        builder.Property(country => country.CreatedOn)
            .HasColumnName("created_on")
            .HasColumnType("DATETIME2")
            .IsRequired();

        builder.Property(country => country.UpdatedOn)
            .HasColumnName("updated_on")
            .HasColumnType("DATETIME2")
            .IsRequired(required: false);

        builder.Property(country => country.IsDisabled)
            .HasColumnName("is_disabled")
            .HasColumnType("BIT")
            .IsRequired();
    }
}
