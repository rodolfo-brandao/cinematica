using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using Cinematica.Core.Models;

namespace Cinematica.Data.EntityTypeConfigurations;

public class UserEntityTypeConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.ToTable("user");

        builder.HasKey(user => user.Id);

        builder.Property(user => user.Id)
            .HasColumnName("id")
            .HasColumnType("UNIQUEIDENTIFIER")
            .IsRequired();

        builder.Property(user => user.Username)
            .HasColumnName("username")
            .HasColumnType("VARCHAR(50)")
            .IsRequired();

        builder.Property(user => user.Email)
            .HasColumnName("email")
            .HasColumnType("VARCHAR(255)")
            .IsRequired();

        builder.Property(user => user.Password)
            .HasColumnName("password")
            .HasColumnType("CHAR(32)")
            .IsRequired();

        builder.Property(user => user.PasswordSalt)
            .HasColumnName("password_salt")
            .HasColumnType("CHAR(16)")
            .IsRequired();

        builder.Property(user => user.Role)
            .HasColumnName("role")
            .HasColumnType("VARCHAR(5)")
            .IsRequired();

        builder.Property(user => user.CreatedOn)
            .HasColumnName("created_on")
            .HasColumnType("DATETIME2")
            .IsRequired();

        builder.Property(user => user.UpdatedOn)
            .HasColumnName("updated_on")
            .HasColumnType("DATETIME2")
            .IsRequired(required: false);

        builder.Property(user => user.IsDisabled)
            .HasColumnName("is_disabled")
            .HasColumnType("BIT")
            .IsRequired();
    }
}
