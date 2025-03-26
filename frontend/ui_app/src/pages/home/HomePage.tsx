import React from 'react';
import { Logo } from "../../components/logo";
import { useLocation, useNavigate } from "react-router-dom";
import { Github, BookOpen } from 'lucide-react';

const FeatureCard = ({ Icon, title, description }) => (
	<div
		className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200">
		<div className="flex items-center mb-4">
			<div className="mr-2 rounded-full p-3">
				<Icon className="w-6 h-6 text-blue-600" />
			</div>
			<h2 className="text-xl font-bold text-gray-800">{title}</h2>
		</div>
		<p className="text-gray-600 ml-16">{description}</p>
	</div>
);

const AssetManagementSVG = () => (
	<svg className="w-full max-w-lg ml-auto" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
		<rect x="50" y="50" width="300" height="200" fill="#E6F3FF" rx="20" />
		<rect x="70" y="70" width="100" height="80" fill="#3B82F6" rx="10" />
		<rect x="190" y="70" width="140" height="30" fill="#93C5FD" rx="5" />
		<rect x="190" y="120" width="140" height="30" fill="#93C5FD" rx="5" />
		<circle cx="120" cy="200" r="30" fill="#60A5FA" />
		<path d="M190 170 L330 170 L330 230 L190 230 Z" fill="#BFDBFE" />
		<line x1="210" y1="190" x2="310" y2="190" stroke="#4B5563" strokeWidth="2" />
		<line x1="210" y1="210" x2="310" y2="210" stroke="#4B5563" strokeWidth="2" />
	</svg>
);

const FolderIcon = ({ className }) => (
	<svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path
			d="M3 7C3 5.89543 3.89543 5 5 5H9L11 7H19C20.1046 7 21 7.89543 21 9V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z"
			stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
	</svg>
);

const TeamIcon = ({ className }) => (
	<svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24"
		stroke="currentColor">
		<path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
			d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
	</svg>
);

const LockIcon = ({ className }) => (
	<svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
		<path
			d="M12 15V17M6 21H18C19.1046 21 20 20.1046 20 19V13C20 11.8954 19.1046 11 18 11H6C4.89543 11 4 11.8954 4 13V19C4 20.1046 4.89543 21 6 21ZM16 11V7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7V11H16Z"
			stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
	</svg>
);

const TopBar = ({repoUrl, docsUrl}) => (
	<nav className="flex justify-between items-center py-3">
		<a href="/" className="flex items-center space-x-2">
			<Logo className="w-8 h-8" />
			<span className="text-2xl font-semibold text-primary">Asset Manager</span>
		</a>
		<div className="flex items-center space-x-6 pr-16">
			<a
				href={repoUrl}
				target="_blank"
				rel="noopener noreferrer"
				className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition duration-300"
			>
				<Github className="w-5 h-5" />
				<span className="hidden md:inline font-semibold">GitHub</span>
			</a>
			<a
				href={docsUrl}
				target="_blank"
				rel="noopener noreferrer"
				className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition duration-300"
			>
				<BookOpen className="w-5 h-5" />
				<span className="hidden md:inline font-semibold">Docs</span>
			</a>
		</div>
	</nav>
);

export const HomePage = () => {
	const location = useLocation();
	const navigate = useNavigate();
	const params = new URLSearchParams(location.search);
	const token = params.get('token');
	const repoUrl: string = import.meta.env.VITE_REPO_URL || '';
	const docsUrl: string = import.meta.env.VITE_DOCS_URL || '';

	/**
	 * Redirect from cli `open asset dashboard`, to be used for authentication in PrivateRoute
	 */
	if (token) {
		navigate(`${"/projects"}?token=${token}`);
	}

	return (
		<div className="w-full bg-gradient-to-b from-slate-100 to-white px-32">
			<TopBar repoUrl={repoUrl} docsUrl={docsUrl} />
			<main className="container mx-auto py-16">
				<div className="flex flex-col md:flex-row items-center">
					<div className="md:w-1/2 text-left md:text-left mb-8 md:mb-0">
						<h1 className="text-4xl md:text-4xl font-bold text-primary mb-4">
							<Logo className="w-16 h-16" />
							Asset Manager
						</h1>
						<h1 className="text-4xl md:text-4xl font-bold text-gray-800 mb-4">Manage Your Digital Assets
							with Ease</h1>
						<p className="text-xl text-gray-600 mb-8">Organize, collaborate, and secure your files in one
							place.</p>
					</div>
					<div className="md:w-1/2 flex justify-end">
						<AssetManagementSVG />
					</div>
				</div>

				<div className="text-center mb-16 -mt-16 flex items-center justify-center">
					<div>
						<Logo className="w-16 h-16 mx-auto mb-12" />
						<div onClick={() => navigate("/login")}
							className="mx-auto flex items-center bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition duration-300 cursor-pointer">
							Sign in to continue
							{/*<MoveRight className="w-6 h-6 ml-2"/>*/}
						</div>
					</div>
				</div>

				<div className="grid md:grid-cols-3 gap-8 px-8">
					<FeatureCard
						Icon={TeamIcon}
						title="Version Control"
						description="Track changes, manage revisions, and collaborate seamlessly with our Git like version control system for data."
					/>
					<FeatureCard
						Icon={FolderIcon}
						title="Organized Storage"
						description="Keep your files structured and easily accessible as you would in your local folder system."
					/>
					<FeatureCard
						Icon={LockIcon}
						title="Secure Access"
						description="Advanced security measures to keep your digital assets safe and protected."
					/>
				</div>
			</main>

			<footer className="bg-gray-100 my-16">
				<div className="container mx-auto px-4 py-8">
					<div className="text-center text-gray-600">
						<p className="mb-4">&copy; 2024 Asset Manager. All rights reserved.</p>
						<div className="flex justify-center space-x-6">
							<a
								href={docsUrl}
								target="_blank"
								rel="noopener noreferrer"
								className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition duration-300"
							>
								<Github className="w-5 h-5" />
								<span>GitHub Repository</span>
							</a>
							<a
								href={repoUrl}
								target="_blank"
								rel="noopener noreferrer"
								className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition duration-300"
							>
								<BookOpen className="w-5 h-5" />
								<span>Documentation</span>
							</a>
						</div>
					</div>
				</div>
			</footer>
		</div>
	);
};
