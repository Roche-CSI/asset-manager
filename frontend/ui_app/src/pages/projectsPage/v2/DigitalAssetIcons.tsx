import React, {ReactComponentElement, useState} from 'react';
import { ReactComponent as Avatar } from "../../../assets/project_icons/avatar.svg"
import { ReactComponent as Avatar1 } from "../../../assets/project_icons/avatar-1.svg"
import { ReactComponent as Avatar2 } from "../../../assets/project_icons/avatar-2.svg"
import { ReactComponent as Avatar3 } from "../../../assets/project_icons/avatar-3.svg"
import { ReactComponent as Avatar4 } from "../../../assets/project_icons/avatar-4.svg"
import { ReactComponent as Avatar5 } from "../../../assets/project_icons/avatar-5.svg"
import { ReactComponent as Avatar6 } from "../../../assets/project_icons/avatar-6.svg"
import { ReactComponent as Avatar7 } from "../../../assets/project_icons/avatar-7.svg"
import { ReactComponent as Avatar8 } from "../../../assets/project_icons/avatar-8.svg"
import { ReactComponent as Avatar9 } from "../../../assets/project_icons/avatar-9.svg"
import { ReactComponent as Avatar10 } from "../../../assets/project_icons/avatar-10.svg"
import { ReactComponent as Avatar11 } from "../../../assets/project_icons/avatar-11.svg"


const DigitalAssetIcons = ({name, size = 32, className = '', index = null}) => {
		if (index != null) {
			switch (index) {
				case 0:
					return <Avatar className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 1:
					return <Avatar1 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 2:
					return <Avatar2 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 3:
					return <Avatar3 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 4:
					return <Avatar4 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 5:
					return <Avatar5 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 6:
					return <Avatar6 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 7:
					return <Avatar7 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 8:
					return <Avatar8 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 9:
					return <Avatar9 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 10:
					return <Avatar10 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				case 11:
					return <Avatar11 className={`inline-block ${className}`} style={{width: size, height: size}}/>;
				default:
					return <Avatar className={`inline-block ${className}`} style={{width: size, height: size}}/>;
			}
		}
		
		const ICONS_MAP = {

		}
		
		const variations = [
			{
				name: 'Original',
				background: '#2c3e50',
				device: '#34495e',
				screen: '#2c3e50',
				asset1: '#f39c12',
				asset2: '#27ae60',
				asset3: '#e74c3c',
				binary: '#95a5a6',
				border: '#34495e'
			},
			{
				name: 'Neon',
				background: '#000000',
				device: '#1a1a1a',
				screen: '#000000',
				asset1: '#ff00ff',
				asset2: '#00ffff',
				asset3: '#ffff00',
				binary: '#00ff00',
				border: '#ffffff'
			},
			{
				name: 'Pastel',
				background: '#f0f0f0',
				device: '#d0d0d0',
				screen: '#ffffff',
				asset1: '#ffb3ba',
				asset2: '#baffc9',
				asset3: '#bae1ff',
				binary: '#ffdfba',
				border: '#d0d0d0'
			},
			{
				name: 'Monochrome',
				background: '#ffffff',
				device: '#cccccc',
				screen: '#ffffff',
				asset1: '#666666',
				asset2: '#999999',
				asset3: '#333333',
				binary: '#000000',
				border: '#000000'
			},
			{
				name: 'Ocean',
				background: '#001f3f',
				device: '#0074D9',
				screen: '#7FDBFF',
				asset1: '#39CCCC',
				asset2: '#3D9970',
				asset3: '#2ECC40',
				binary: '#01FF70',
				border: '#0074D9'
			},
			{
				name: 'Sunset',
				background: '#FF851B',
				device: '#FF4136',
				screen: '#FFDC00',
				asset1: '#F012BE',
				asset2: '#B10DC9',
				asset3: '#85144b',
				binary: '#FFFFFF',
				border: '#FF4136'
			}
		];
		
		const renderPixelArt = (colors) => (
			<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width={size} height={size}>
				<defs>
					<clipPath id="rounded-mask">
						<rect width="32" height="32" rx="4" ry="4"/>
					</clipPath>
				</defs>
				<g clipPath="url(#rounded-mask)">
					<rect width="32" height="32" fill={colors.background}/>
					<rect x="4" y="8" width="24" height="16" fill={colors.device}/>
					<rect x="6" y="10" width="20" height="12" fill={colors.screen}/>
					
					{/* Asset 1 */}
					<rect x="8" y="12" width="6" height="6" fill={colors.asset1}/>
					<rect x="9" y="13" width="4" height="4" fill={colors.asset1} fillOpacity="0.7"/>
					
					{/* Asset 2 */}
					<rect x="16" y="12" width="4" height="6" fill={colors.asset2}/>
					<rect x="17" y="13" width="2" height="4" fill={colors.asset2} fillOpacity="0.7"/>
					
					{/* Asset 3 */}
					<rect x="22" y="12" width="4" height="4" fill={colors.asset3}/>
					<rect x="23" y="13" width="2" height="2" fill={colors.asset3} fillOpacity="0.7"/>
					
					{/* Binary */}
					<rect x="8" y="20" width="16" height="2" fill={colors.binary}/>
					
					{/* Connections */}
					<rect x="10" y="18" width="1" height="2" fill={colors.asset1}/>
					<rect x="17" y="18" width="1" height="2" fill={colors.asset2}/>
					<rect x="23" y="16" width="1" height="4" fill={colors.asset3}/>
				</g>
			</svg>
		);
		
		const type = ICONS_MAP[name] || 'Original';
		const colors = variations.filter((v) => v.name === type)[0]
		return (
			<div className={`inline-block ${className}`} style={{width: size, height: size}}>
				{renderPixelArt(colors)}
			</div>
		);
	}
;

export default DigitalAssetIcons;
