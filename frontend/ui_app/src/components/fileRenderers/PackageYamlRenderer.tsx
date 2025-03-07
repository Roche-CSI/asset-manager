import React, { useMemo } from 'react';
import { GitBranch, GitCommit, Package, Calendar, User, Settings } from 'lucide-react';

const PackageYamlRenderer = ({ yaml }) => {
    const packageObject = yaml.packages;
    const envRows = useMemo(() => entriesToRows(yaml), [yaml]);
    const packageRows = useMemo(() => {
        const rows = entriesToRows(packageObject);
        return rows.sort((a, b) => (a.name > b.name ? 1 : -1));
    }, [packageObject]);
    
    return (
        <div className="max-w-4xl mx-auto p-6 space-y-6 bg-white rounded-lg shadow-lg">
            {/* Header Section */}
            <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                <div className="flex items-center space-x-4">
                    <Package className="h-6 w-6 text-blue-600" />
                    <h1 className="text-2xl font-bold text-gray-800">{yaml.name}</h1>
                </div>
                <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                    <div className="flex items-center">
                        <User className="h-4 w-4 mr-2" />
                        {yaml.user}
                    </div>
                    <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-2" />
                        {yaml.date}
                    </div>
                </div>
            </div>
            
            {/* Environment Section */}
            <div className="space-y-2">
                <h2 className="text-lg font-semibold text-gray-700 flex items-center">
                    <Settings className="h-5 w-5 mr-2 text-gray-600" />
                    Environment
                </h2>
                <div className="bg-gray-50 p-4 rounded-lg">
                    {renderEnvironment(envRows.find(row => row.name === 'env')?.value || [])}
                </div>
            </div>
            
            {/* Packages Section */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-700">Packages</h2>
                <div className="grid gap-4 md:grid-cols-2">
                    {packageRows.map((pkg) => (
                        <PackageCard key={pkg.name} package={pkg} />
                    ))}
                </div>
            </div>
        </div>
    );
};

const PackageCard = ({ package: pkg }) => {
    const getPackageInfo = (value) => {
        const info = {};
        value.forEach(item => {
            info[item.name] = item.value;
        });
        return info;
    };
    
    const info = getPackageInfo(pkg.value);
    
    return (
        <div className="bg-gray-50 p-4 rounded-lg hover:shadow-md transition-shadow">
            <h3 className="text-lg font-semibold text-blue-600 mb-3">{pkg.name}</h3>
            <div className="space-y-2 text-sm">
                <div className="flex items-center text-gray-600">
                    <GitBranch className="h-4 w-4 mr-2" />
                    <span className="font-medium mr-2">Branch:</span>
                    {info.branch}
                </div>
                <div className="flex items-center text-gray-600">
                    <GitCommit className="h-4 w-4 mr-2" />
                    <span className="font-medium mr-2">Commit:</span>
                    <span className="font-mono text-xs">{info.commit?.slice(0, 7)}</span>
                </div>
                <div className="flex items-center text-gray-600">
                    <Package className="h-4 w-4 mr-2" />
                    <span className="font-medium mr-2">Version:</span>
                    {info.version}
                </div>
            </div>
        </div>
    );
};

const renderEnvironment = (envData) => {
    return (
        <div className="grid grid-cols-2 gap-4">
            {envData.map((item, index) => (
                <div key={index} className="flex items-center text-gray-600">
                    <span className="font-medium mr-2">{item.name}:</span>
                    <span>{String(item.value)}</span>
                </div>
            ))}
        </div>
    );
};

const entriesToRows = (data) => {
    let res = [];
    for (let x in data) {
        if (x === "packages") continue;
        const row = {
            name: x,
            value: typeof data[x] === 'object' ? entriesToRows(data[x]) : data[x]
        };
        res.push(row);
    }
    return res;
};

export default PackageYamlRenderer;
