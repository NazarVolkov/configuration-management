#include "app.h"



#include <stdexcept>
#include <tinyxml2.h>

namespace {
using tinyxml2::XMLElement;

const XMLElement* select_group(const XMLElement* deps, const std::string& framework) {
    if (!deps || !deps->FirstChildElement("group")) {
        return deps;
    }
    const XMLElement* fallback = nullptr;
    for (auto group = deps->FirstChildElement("group"); group; group = group->NextSiblingElement("group")) {
        const char* target = group->Attribute("targetFramework");
        if (!target || !*target) {
            fallback = group;
        } else if (framework == target) {
            return group;
        }
    }
    if (fallback) {
        return fallback;
    }
    throw std::runtime_error("Framework group not found: " + framework);
}
}  // namespace

Requirements read_dependencies(const std::string& xml, const std::string& framework) {
    tinyxml2::XMLDocument document;
    if (document.Parse(xml.data(), xml.size()) != tinyxml2::XML_SUCCESS) {
        throw std::runtime_error("Invalid nuspec XML.");
    }
    const auto package = document.FirstChildElement("package");
    const auto metadata = package ? package->FirstChildElement("metadata") : nullptr;
    if (!metadata) {
        throw std::runtime_error("No package metadata in nuspec.");
    }

    Requirements result;
    const auto group = select_group(metadata->FirstChildElement("dependencies"), framework);
    if (!group) {
        return result;
    }
    for (auto dep = group->FirstChildElement("dependency"); dep; dep = dep->NextSiblingElement("dependency")) {
        const char* id = dep->Attribute("id");
        const char* version = dep->Attribute("version");
        if (!id || !valid_name(id, false)) {
            throw std::runtime_error("Invalid dependency ID in nuspec.");
        }
        result.emplace_back(id, version ? version : "");
    }
    return result;
}



#include <algorithm>
#include <cctype>
#include <stdexcept>

#include <json.hpp>

namespace {
using nlohmann::json;

bool is_flat_container(const json& type) {
    const auto resource = "PackageBaseAddress/3.0.0";
    return type == resource || (type.is_array() && std::find(type.begin(), type.end(), resource) != type.end());
}

std::string package_base(const std::string& index_url) {
    const auto index = json::parse(download(index_url));
    for (const auto& resource : index.at("resources")) {
        if (!is_flat_container(resource.at("@type"))) {
            continue;
        }
        auto base = resource.at("@id").get<std::string>();
        if (!valid_url(base) || base.find('?') != std::string::npos) {
            throw std::runtime_error("Invalid PackageBaseAddress URL.");
        }
        if (base.back() != '/') {
            base += '/';
        }
        return base;
    }
    throw std::runtime_error("NuGet index has no PackageBaseAddress/3.0.0.");
}
}  // namespace

std::string lower_name(std::string value) {
    for (char& item : value) {
        item = static_cast<char>(std::tolower(static_cast<unsigned char>(item)));
    }
    return value;
}

Nuget::Nuget(const Settings& settings)
    : base_(package_base(settings.repository)), framework_(settings.framework) {}

const Packages& Nuget::versions(const std::string& id) {
    auto found = versions_.find(id);
    if (found == versions_.end()) {
        const auto index = json::parse(download(base_ + id + "/index.json"));
        found = versions_.emplace(id, index.at("versions").get<Packages>()).first;
    }
    return found->second;
}

std::string Nuget::root(const Settings& settings) {
    const auto id = lower_name(settings.package);
    const auto& version = settings.version;
    return id + "@" + choose_version(versions(id), version.empty() ? "" : "[" + version + "]", version.empty());
}

Packages Nuget::dependencies(const std::string& package) {
    const auto found = dependencies_.find(package);
    if (found != dependencies_.end()) {
        return found->second;
    }
    const auto separator = package.find('@');
    const auto id = package.substr(0, separator);
    const auto version = package.substr(separator + 1);
    const auto xml = download(base_ + id + "/" + version + "/" + id + ".nuspec");
    Packages result;
    for (const auto& [name, range] : read_dependencies(xml, framework_)) {
        const auto dependency = lower_name(name);
        const auto node = dependency + "@" + choose_version(versions(dependency), range);
        if (std::find(result.begin(), result.end(), node) == result.end()) {
            result.push_back(node);
        }
    }
    dependencies_.emplace(package, result);
    return result;
}
