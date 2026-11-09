// crucible-ai: bridge from the Crucible companion to Apple's on-device
// Foundation Models (Apple Intelligence).
//
//   crucible-ai --status        prints {"available": bool, "reason": "..."}
//   crucible-ai < request.json  streams the model's answer to stdout
//
// request.json: {"instructions": "...", "prompt": "...", "temperature": 0.3}

import Foundation
import FoundationModels

struct Request: Decodable {
    let instructions: String
    let prompt: String
    let temperature: Double?
}

func statusJSON() -> String {
    let model = SystemLanguageModel.default
    var available = false
    var reason = "available"
    switch model.availability {
    case .available:
        available = true
    case .unavailable(let why):
        switch why {
        case .deviceNotEligible: reason = "This Mac doesn't support Apple Intelligence."
        case .appleIntelligenceNotEnabled: reason = "Apple Intelligence is turned off. Enable it in System Settings → Apple Intelligence & Siri."
        case .modelNotReady: reason = "The on-device model is still downloading. Try again in a few minutes."
        @unknown default: reason = "Apple Intelligence is unavailable."
        }
    }
    let obj: [String: Any] = ["available": available, "reason": reason, "contextSize": available ? model.contextSize : 0]
    let data = try! JSONSerialization.data(withJSONObject: obj)
    return String(data: data, encoding: .utf8)!
}

func fail(_ msg: String) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(1)
}

@main
struct CrucibleAI {
    static func main() async {
        if CommandLine.arguments.contains("--status") {
            print(statusJSON())
            return
        }
        let input = FileHandle.standardInput.readDataToEndOfFile()
        guard let req = try? JSONDecoder().decode(Request.self, from: input) else { fail("Invalid request") }
        guard case .available = SystemLanguageModel.default.availability else { fail("Apple Intelligence is unavailable on this Mac.") }

        let session = LanguageModelSession(instructions: req.instructions)
        let options = GenerationOptions(temperature: req.temperature ?? 0.3)
        var printed = 0
        do {
            let stream = session.streamResponse(to: req.prompt, options: options)
            for try await snapshot in stream {
                let text = snapshot.content
                if text.count > printed {
                    let idx = text.index(text.startIndex, offsetBy: printed)
                    let delta = String(text[idx...])
                    FileHandle.standardOutput.write(delta.data(using: .utf8)!)
                    printed = text.count
                }
            }
        } catch let e as LanguageModelSession.GenerationError {
            switch e {
            case .exceededContextWindowSize:
                fail("The request was too long for the on-device model. Try asking about a smaller part of your code.")
            case .guardrailViolation:
                fail("The on-device model declined to answer that. Try rephrasing the question.")
            default:
                fail("Generation failed: \(e.localizedDescription)")
            }
        } catch {
            fail("Generation failed: \(error.localizedDescription)")
        }
    }
}
