using System;
using System.Drawing;
using System.IO;
using System.Text;

namespace Cyotek.Windows.Forms
{
  // Cyotek Color Picker controls library
  // Copyright © 2013-2015 Cyotek Ltd.
  // http://cyotek.com/blog/tag/colorpicker

  // Licensed under the MIT License. See license.txt for the full text.

  // If you use this code in your applications, donations or attribution are welcome

  /// <summary>
  /// Serializes and deserializes color palettes into and from the Jasc palette format.
  /// </summary>
  public class JascPaletteSerializer : PaletteSerializer
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
      get { return "JASC Palette"; }
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
        using (StreamReader reader = new StreamReader(stream))
        {
          string header;
          string version;

          // check signature
          header = reader.ReadLine();
          version = reader.ReadLine();

          result = (header == "JASC-PAL" && version == "0100");
        }
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

      using (StreamReader reader = new StreamReader(stream))
      {
        string header;
        string version;
        int colorCount;

        // check signature
        header = reader.ReadLine();
        version = reader.ReadLine();

        if (header != "JASC-PAL" || version != "0100")
        {
          throw new InvalidDataException("Invalid palette file");
        }

        colorCount = Convert.ToInt32(reader.ReadLine());
        for (int i = 0; i < colorCount; i++)
        {
          int r;
          int g;
          int b;
          string data;
          string[] parts;

          data = reader.ReadLine();
          parts = !string.IsNullOrEmpty(data) ? data.Split(new[]
                                                           {
                                                             ' ', '\t'
                                                           }, StringSplitOptions.RemoveEmptyEntries) : new string[0];

          if (!int.TryParse(parts[0], out r) || !int.TryParse(parts[1], out g) || !int.TryParse(parts[2], out b))
          {
            throw new InvalidDataException(string.Format("Invalid palette contents found with data '{0}'", data));
          }

          results.Add(Color.FromArgb(r, g, b));
        }
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

      using (StreamWriter writer = new StreamWriter(stream, Encoding.UTF8))
      {
        writer.WriteLine("JASC-PAL");
        writer.WriteLine("0100");
        writer.WriteLine(palette.Count);
        foreach (Color color in palette)
        {
          writer.Write("{0} ", color.R);
          writer.Write("{0} ", color.G);
          writer.Write("{0} ", color.B);
          writer.WriteLine();
        }
      }
    }

    #endregion
  }
}
