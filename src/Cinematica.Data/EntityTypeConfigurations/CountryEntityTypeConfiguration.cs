using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Cinematica.Core.Models;

namespace Cinematica.Data.EntityTypeConfigurations;

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

        builder.Property(country => country.CreatedAt)
            .HasColumnName("created_on")
            .HasColumnType("DATETIME2")
            .IsRequired();

        builder.Property(country => country.UpdatedAt)
            .HasColumnName("updated_on")
            .HasColumnType("DATETIME2")
            .IsRequired(required: false);

        builder.Property(country => country.IsDisabled)
            .HasColumnName("is_disabled")
            .HasColumnType("BIT")
            .IsRequired();
    }
}
