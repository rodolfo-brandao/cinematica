using System.Diagnostics.CodeAnalysis;
using Cinematica.Core.Models.Abstract;

namespace Cinematica.Core.Models.Nulls;

[ExcludeFromCodeCoverage]
public sealed class NullUser : User, INullObject
{
}
