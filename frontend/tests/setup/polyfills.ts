/**
 * Test environment polyfills
 * This file runs BEFORE any test files are loaded
 */

import { TextEncoder, TextDecoder } from 'util'
import { ReadableStream, WritableStream, TransformStream } from 'stream/web'
import 'whatwg-fetch'

// Polyfill TextEncoder/TextDecoder for MSW
global.TextEncoder = TextEncoder
global.TextDecoder = TextDecoder as any

// Polyfill Streams API for MSW
global.ReadableStream = ReadableStream as any
global.WritableStream = WritableStream as any
global.TransformStream = TransformStream as any
