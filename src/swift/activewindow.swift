// Adapted from https://github.com/sindresorhus/active-win/blob/main/Sources/active-win/main.swift under the MIT license
//
// Original Copyright (c) Sindre Sorhus <sindresorhus@gmail.com> (https://sindresorhus.com)
//
// Adapted by Harry Jubb <https://github.com/harryjubb> (https://harryjubb.dev)

import AppKit

func toJson<T>(_ data: T) throws -> String {
    let json = try JSONSerialization.data(withJSONObject: data)
    return String(data: json, encoding: .utf8)!
}

func showErrorAndExit(error: String) -> Void {
    print("{\"error\": \"\(error)\"}")
    exit(1)
}

// Show the system prompt if there's no permission.
let hasScreenRecordingPermission = CGDisplayStream(
    dispatchQueueDisplay: CGMainDisplayID(),
    outputWidth: 1,
    outputHeight: 1,
    pixelFormat: Int32(kCVPixelFormatType_32BGRA),
    properties: nil,
    queue: DispatchQueue.global(),
    handler: { _, _, _, _ in }
) != nil

let hasAccessibilityPermission = AXIsProcessTrustedWithOptions(["AXTrustedCheckOptionPrompt": true] as CFDictionary)

// Show accessibility permission prompt if needed. Required to get the complete window title.
if !hasAccessibilityPermission {
    showErrorAndExit(error: "Listing window details requires the accessibility permission in “System Preferences › Security & Privacy › Privacy › Accessibility”.")
}

// Show screen recording permission prompt if needed. Required to get the complete window title.
if !hasScreenRecordingPermission {
    showErrorAndExit(error: "Listing window details requires the screen recording permission in “System Preferences › Security & Privacy › Privacy › Screen Recording”.")
}

guard
    let frontmostAppPID = NSWorkspace.shared.frontmostApplication?.processIdentifier,
    let windows = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]]
else {
    showErrorAndExit(error: "No windows found")
    exit(1)
}

for window in windows {
    let windowOwnerPID = window[kCGWindowOwnerPID as String] as! pid_t // Documented to always exist.
    if windowOwnerPID != frontmostAppPID {
        continue
    }
    
    // Skip transparent windows, like with Chrome.
    if (window[kCGWindowAlpha as String] as! Double) == 0 { // Documented to always exist.
        continue
    }

    let bounds = CGRect(dictionaryRepresentation: window[kCGWindowBounds as String] as! CFDictionary)! // Documented to always exist.
    
    // Skip tiny windows, like the Chrome link hover statusbar.
    let minWinSize: CGFloat = 50
    if bounds.width < minWinSize || bounds.height < minWinSize {
        continue
    }
    
    // This should not fail as we're only dealing with apps, but we guard it just to be safe.
    guard let app = NSRunningApplication(processIdentifier: windowOwnerPID) else {
        continue
    }
    
    let appName = window[kCGWindowOwnerName as String] as? String ?? app.bundleIdentifier ?? "Unknown"
    let windowTitle = window[kCGWindowName as String] as? String ?? "unknown"
    
    let output: [String: Any] = [
        "title": windowTitle,
        "id": window[kCGWindowNumber as String] as! Int, // Documented to always exist.
        "owner": [
            "name": appName,
            "processId": windowOwnerPID,
            "bundleId": app.bundleIdentifier ?? "nobundleid", // I don't think this could happen, but we also don't want to crash.
            "path": app.bundleURL?.path ?? "nopath" // I don't think this could happen, but we also don't want to crash.
        ]
    ]
    
    guard let string = try? toJson(output) else {
        showErrorAndExit(error: "Unable to convert output to JSON")
        exit(1)
    }
    
    print(string)
    exit(0)
}
