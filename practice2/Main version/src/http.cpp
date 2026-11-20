#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <winhttp.h>

#include "app.h"

#include <array>
#include <filesystem>
#include <stdexcept>

namespace {
constexpr int timeout_ms = 20000;
constexpr unsigned ok_status = 200;
constexpr std::size_t response_limit = 64 * 1024 * 1024;

void check(BOOL result, const char* action) {
    if (!result) {
        throw std::runtime_error(std::string(action) + ": WinHTTP error " + std::to_string(GetLastError()));
    }
}

struct Handle {
    HINTERNET value;

    explicit Handle(HINTERNET handle) : value(handle) { check(value != nullptr, "Open HTTP handle"); }
    ~Handle() { WinHttpCloseHandle(value); }
    Handle(const Handle&) = delete;
    Handle& operator=(const Handle&) = delete;
};

std::string body(HINTERNET request) {
    DWORD status = 0;
    DWORD size = sizeof(status);
    check(WinHttpQueryHeaders(request, WINHTTP_QUERY_STATUS_CODE | WINHTTP_QUERY_FLAG_NUMBER,
                             nullptr, &status, &size, nullptr), "Read HTTP status");
    if (status != ok_status) {
        throw std::runtime_error("HTTP status " + std::to_string(status));
    }

    std::string data;
    std::array<char, 8192> chunk{};
    DWORD received = 0;
    do {
        check(WinHttpReadData(request, chunk.data(), static_cast<DWORD>(chunk.size()), &received), "Read HTTP");
        if (data.size() + received > response_limit) {
            throw std::runtime_error("HTTP response is too large.");
        }
        data.append(chunk.data(), received);
    } while (received != 0);
    return data;
}
}  // namespace

std::string download(const std::string& url) {
    if (!valid_url(url)) {
        throw std::runtime_error("Invalid HTTP(S) URL: " + url);
    }
    const auto wide = std::filesystem::u8path(url).wstring();
    URL_COMPONENTS parts{};
    parts.dwStructSize = sizeof(parts);
    parts.dwHostNameLength = DWORD(-1);
    parts.dwUrlPathLength = DWORD(-1);
    parts.dwExtraInfoLength = DWORD(-1);
    check(WinHttpCrackUrl(wide.c_str(), 0, 0, &parts), "Parse URL");

    const std::wstring host(parts.lpszHostName, parts.dwHostNameLength);
    std::wstring path;
    if (parts.dwUrlPathLength) {
        path.assign(parts.lpszUrlPath, parts.dwUrlPathLength);
    }
    if (path.empty()) {
        path = L"/";
    }
    if (parts.dwExtraInfoLength) {
        path.append(parts.lpszExtraInfo, parts.dwExtraInfoLength);
    }

    const Handle session(WinHttpOpen(L"nuget-graph/1", WINHTTP_ACCESS_TYPE_AUTOMATIC_PROXY,
                                     WINHTTP_NO_PROXY_NAME, WINHTTP_NO_PROXY_BYPASS, 0));
    check(WinHttpSetTimeouts(session.value, timeout_ms, timeout_ms, timeout_ms, timeout_ms), "Set HTTP timeouts");
    const Handle connection(WinHttpConnect(session.value, host.c_str(), parts.nPort, 0));
    const DWORD flags = parts.nScheme == INTERNET_SCHEME_HTTPS ? WINHTTP_FLAG_SECURE : 0;
    const Handle request(WinHttpOpenRequest(connection.value, L"GET", path.c_str(),
                                           nullptr, WINHTTP_NO_REFERER, WINHTTP_DEFAULT_ACCEPT_TYPES, flags));
    check(WinHttpSendRequest(request.value, WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                             WINHTTP_NO_REQUEST_DATA, 0, 0, 0), "Send HTTP request");
    check(WinHttpReceiveResponse(request.value, nullptr), "Receive HTTP response");
    return body(request.value);
}
