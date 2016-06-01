//
//  main.m
//  color-pick
//
//  Created by Johan Nordberg on 2011-09-20.
//  Copyright 2011 FFFF00 Agents AB. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <AppKit/AppKit.h>

@interface NSColor (Additions)
+(NSColor *)colorFromString:(NSString *)colorRepresentation;

-(NSString *)toHexString;

@end


@implementation NSColor (Additions)
+(NSColor *)colorFromString:(NSString *)colorRepresentation {

  if([colorRepresentation length] != 8)
    return [NSColor whiteColor];

  NSString* rString = [colorRepresentation substringWithRange:NSMakeRange(0, 2)];
  NSString* gString = [colorRepresentation substringWithRange:NSMakeRange(2, 2)];
  NSString* bString = [colorRepresentation substringWithRange:NSMakeRange(4, 2)];
  NSString* aString = [colorRepresentation substringWithRange:NSMakeRange(6, 2)];

  return [NSColor colorWithCalibratedRed: strtol([rString UTF8String], NULL, 16) / 255.0
                                   green: strtol([gString UTF8String], NULL, 16) / 255.0
                                    blue: strtol([bString UTF8String], NULL, 16) / 255.0
                                   alpha: strtol([aString UTF8String], NULL, 16) / 255.0];
}

-(NSString *)toHexString {
    NSColor *color = [self colorUsingColorSpaceName: NSCalibratedRGBColorSpace];

    return [NSString stringWithFormat: @"#%02X%02X%02X%02X",
                        (unsigned int)(255 * [color redComponent]),
                        (unsigned int)(255 * [color greenComponent]),
                        (unsigned int)(255 * [color blueComponent]),
                        (unsigned int)(255 * [color alphaComponent])];
}

@end


@interface Picker : NSObject <NSApplicationDelegate, NSWindowDelegate> {
  NSColorPanel *panel; // weak ref
}

- (void)show;
- (void)writeColor;
- (void)exit;

@end

@implementation Picker

- (void)show {
  // setup panel and its accessory view

  NSView *accessoryView = [[NSView alloc] initWithFrame:(NSRect){{0, 0}, {220, 30}}];

  NSButton *button = [[NSButton alloc] initWithFrame:(NSRect){{110, 4}, {110 - 8, 24}}];
  [button setButtonType:NSMomentaryPushInButton];
  [button setBezelStyle:NSRoundedBezelStyle];
  button.title = @"Pick";
  button.action = @selector(writeColor);
  button.target = self;

  NSButton *cancelButton = [[NSButton alloc] initWithFrame:(NSRect){{8, 4}, {110 - 8, 24}}];
  [cancelButton setButtonType:NSMomentaryPushInButton];
  [cancelButton setBezelStyle:NSRoundedBezelStyle];
  cancelButton.title = @"Cancel";
  cancelButton.action = @selector(exit);
  cancelButton.target = self;

  [accessoryView addSubview:[button autorelease]];
  [accessoryView addSubview:[cancelButton autorelease]];

  panel = [NSColorPanel sharedColorPanel];
  [panel setDelegate:self];
  [panel setShowsAlpha:YES]; // TODO: support for rgba() output values
  [panel setAccessoryView:[accessoryView autorelease]];
  [panel setDefaultButtonCell:[button cell]];

  // load user settings
  NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
  NSString *color = [defaults stringForKey:@"startColor"];
  if (color != nil) {
    [panel setColor:[NSColor colorFromString:color]];
  }
  [panel setMode:[defaults integerForKey:@"mode"]]; // will be 0 if not set, wich is NSGrayModeColorPanel

  // show panel
  [panel makeKeyAndOrderFront:self];
  //[NSApp runModalForWindow:panel]; // resets panel position
}

- (void)writeColor {
  NSString *hex = [panel.color toHexString];

  // save color and current mode to defaults
  NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
  [defaults setObject:hex forKey:@"startColor"];
  [defaults setInteger:panel.mode forKey:@"mode"];
  [defaults synchronize]; // force a save since we are exiting

  // write color to stdout
  NSFileHandle *stdOut = [NSFileHandle fileHandleWithStandardOutput];
  [stdOut writeData:[hex dataUsingEncoding:NSASCIIStringEncoding]];

  [self exit];
}


- (void)exit {
  [panel close];
}

// panel delegate methods

- (void)windowWillClose:(NSNotification *)notification {
  [NSApp terminate:self];
}

// application delegate methods

- (void)applicationDidFinishLaunching:(NSNotification*)aNotification {
  ProcessSerialNumber psn = {0, kCurrentProcess};
  TransformProcessType(&psn, kProcessTransformToForegroundApplication);
  SetFrontProcess(&psn);
  [self show];
}

- (BOOL) applicationShouldTerminateAfterLastWindowClosed:(NSApplication *) theApplication {
  return YES;
}

@end

int main (int argc, const char * argv[]) {
  NSAutoreleasePool * pool = [[NSAutoreleasePool alloc] init];

  if(argc == 2){
    NSString* color = [NSString stringWithUTF8String:argv[1]];
    NSString* colorWithoutHash = [color stringByReplacingOccurrencesOfString:@"#"
                                     withString:@""];
    [[NSUserDefaults standardUserDefaults] setObject:colorWithoutHash forKey:@"startColor"];
    [[NSUserDefaults standardUserDefaults] synchronize];
  }

  NSApplication *app = [NSApplication sharedApplication];
  app.delegate = [[[Picker alloc] init] autorelease];
  [app run];
  [pool drain];
  return 0;
}
