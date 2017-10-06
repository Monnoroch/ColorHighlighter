using System.IO;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  /// <summary>
  /// Serializes and deserializes color palettes into and from other documents.
  /// </summary>
  public interface IPaletteSerializer
  {
    #region Properties

    /// <summary>
    /// Gets a value indicating whether this serializer can be used to read palettes.
    /// </summary>
    /// <value><c>true</c> if palettes can be read using this serializer; otherwise, <c>false</c>.</value>
    bool CanRead { get; }

    /// <summary>
    /// Gets a value indicating whether this serializer can be used to write palettes.
    /// </summary>
    /// <value><c>true</c> if palettes can be written using this serializer; otherwise, <c>false</c>.</value>
    bool CanWrite { get; }

    /// <summary>
    /// Gets the default extension for files generated with this palette format.
    /// </summary>
    /// <value>The default extension for files generated with this palette format.</value>
    string DefaultExtension { get; }

    /// <summary>
    /// Gets a descriptive name of the palette format
    /// </summary>
    /// <value>The descriptive name of the palette format.</value>
    string Name { get; }

    #endregion

    #region Methods

    /// <summary>
    /// Determines whether this instance can read palette data from the specified stream.
    /// </summary>
    /// <param name="stream">The stream.</param>
    /// <returns><c>true</c> if this instance can read palette data from the specified stream; otherwise, <c>false</c>.</returns>
    bool CanReadFrom(Stream stream);

    /// <summary>
    /// Deserializes the <see cref="ColorCollection"/> contained by the specified <see cref="Stream"/>.
    /// </summary>
    /// <param name="stream">The <see cref="Stream"/> that contains the palette to deserialize.</param>
    /// <returns>The <see cref="ColorCollection"/> being deserialized.</returns>
    ColorCollection Deserialize(Stream stream);

    /// <summary>
    /// Serializes the specified <see cref="ColorCollection"/> and writes the palette to a file using the specified <see cref="Stream"/>.
    /// </summary>
    /// <param name="stream">The <see cref="Stream"/> used to write the palette.</param>
    /// <param name="palette">The <see cref="ColorCollection"/> to serialize.</param>
    void Serialize(Stream stream, ColorCollection palette);

    #endregion
  }
}
