import React from 'react';
import styles from './documentation.module.scss';

function DocumentHeader() {
    return (
        <div>
            <h4 className={styles.pageHeader}>Documentation</h4>
            <div className={styles.description}>
                <p>Below you will find a quick start guide for the asset manager's command line interface.</p>
                <p>If you are interested to learn more, please read the full document
                    <a href="" target="_blank" rel="noreferrer"
                        className='text-primary'>
                        here.
                    </a>
                </p>
            </div>
        </div>
    )
}

export default React.memo(DocumentHeader);