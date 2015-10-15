using System;
using System.Drawing;
using System.IO;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  /// <summary>
  /// Serializes and deserializes 8bit color palettes from raw byte data.
  /// </summary>
  public class RawPaletteSerializer : PaletteSerializer
  {
    #region Overridden Properties

    /// <summary>
    /// Gets the default extension for files generated with this palette format.
    /// </summary>
    /// <value>The default extension for files generated with this palette format.</value>
    public override string DefaultExtension
    {
      get { return "pal"; }
    }

    /// <summary>
    /// Gets a descriptive name of the palette format
    /// </summary>
    /// <value>The descriptive name of the palette format.</value>
    public override string Name
    {
      get { return "Raw Palette"; }
    }

    #endregion

    #region Overridden Methods

    /// <summary>
    /// Determines whether this instance can read palette from data the specified stream.
    /// </summary>
    /// <param name="stream">The stream.</param>
    /// <returns><c>true</c> if this instance can read palette data from the specified stream; otherwise, <c>false</c>.</returns>
    public override bool CanReadFrom(Stream stream)
    {
      bool result;

      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      try
      {
        result = stream.Length % 3 == 0;
      }
      catch
      {
        result = false;
      }

      return result;
    }

    /// <summary>
    /// Deserializes the <see cref="ColorCollection" /> contained by the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> that contains the palette to deserialize.</param>
    /// <returns>The <see cref="ColorCollection" /> being deserialized.</returns>
    public override ColorCollection Deserialize(Stream stream)
    {
      ColorCollection results;

      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      results = new ColorCollection();

      for (int i = 0; i < stream.Length / 3; i++)
      {
        int r;
        int g;
        int b;

        r = stream.ReadByte();
        g = stream.ReadByte();
        b = stream.ReadByte();

        results.Add(Color.FromArgb(r, g, b));
      }

      return results;
    }

    /// <summary>
    /// Serializes the specified <see cref="ColorCollection" /> and writes the palette to a file using the specified <see cref="Stream" />.
    /// </summary>
    /// <param name="stream">The <see cref="Stream" /> used to write the palette.</param>
    /// <param name="palette">The <see cref="ColorCollection" /> to serialize.</param>
    public override void Serialize(Stream stream, ColorCollection palette)
    {
      if (stream == null)
      {
        throw new ArgumentNullException("stream");
      }

      if (palette == null)
      {
        throw new ArgumentNullException("palette");
      }

      foreach (Color color in palette)
      {
        stream.WriteByte(color.R);
        stream.WriteByte(color.G);
        stream.WriteByte(color.B);
      }

      stream.Flush();
    }

    #endregion

    #region Private Members

    private int ReadInt(Stream stream)
    {
      byte[] buffer;

      // big endian conversion: http://stackoverflow.com/a/14401341/148962

      buffer = new byte[4];
      stream.Read(buffer, 0, buffer.Length);

      return (buffer[0] << 24) | (buffer[1] << 16) | (buffer[2] << 8) | buffer[3];
    }

    #endregion
  }
}
