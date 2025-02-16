import { useState, useEffect } from 'react';
import {
    Box,
    Autocomplete,
    TextField,
} from '@mui/material';
import { AirtableIntegration } from './integrations/airtable';
import { NotionIntegration } from './integrations/notion';
import { HubSpotIntegration } from './integrations/hubspot';
import { DataForm } from './data-form';
import logger from './services/logger';

const integrationMapping = {
    'Notion': NotionIntegration,
    'Airtable': AirtableIntegration,
    'HubSpot': HubSpotIntegration,
};

export const IntegrationForm = () => {
    const [integrationParams, setIntegrationParams] = useState({});
    const [user, setUser] = useState('TestUser');
    const [org, setOrg] = useState('TestOrg');
    const [currType, setCurrType] = useState(null);
    const CurrIntegration = integrationMapping[currType];

    // Log component mount
    useEffect(() => {
        logger.info('IntegrationForm', 'COMPONENT_MOUNT');
        return () => {
            logger.info('IntegrationForm', 'COMPONENT_UNMOUNT');
        };
    }, []);

    // Log integration type changes
    useEffect(() => {
        if (currType) {
            logger.info('IntegrationForm', 'INTEGRATION_TYPE_CHANGED', {
                type: currType,
                user_id: user,
                org_id: org
            });
        }
    }, [currType, user, org]);

    // Log integration params changes
    useEffect(() => {
        if (integrationParams.type) {
            logger.info('IntegrationForm', 'INTEGRATION_PARAMS_UPDATED', {
                type: integrationParams.type,
                has_credentials: Boolean(integrationParams.credentials)
            });
        }
    }, [integrationParams]);

    const handleUserChange = (e) => {
        const newUser = e.target.value;
        logger.logUserInteraction('IntegrationForm', 'USER_CHANGE', {
            previous: user,
            new: newUser
        });
        setUser(newUser);
    };

    const handleOrgChange = (e) => {
        const newOrg = e.target.value;
        logger.logUserInteraction('IntegrationForm', 'ORG_CHANGE', {
            previous: org,
            new: newOrg
        });
        setOrg(newOrg);
    };

    const handleIntegrationTypeChange = (e, value) => {
        logger.logUserInteraction('IntegrationForm', 'INTEGRATION_TYPE_SELECT', {
            selected_type: value,
            user_id: user,
            org_id: org
        });
        setCurrType(value);
    };

  return (
    <Box display='flex' justifyContent='center' alignItems='center' flexDirection='column' sx={{ width: '100%' }}>
        <Box display='flex' flexDirection='column'>
        <TextField
            label="User"
            value={user}
            onChange={handleUserChange}
            sx={{mt: 2}}
        />
        <TextField
            label="Organization"
            value={org}
            onChange={handleOrgChange}
            sx={{mt: 2}}
        />
        <Autocomplete
            id="integration-type"
            options={Object.keys(integrationMapping)}
            sx={{ width: 300, mt: 2 }}
            renderInput={(params) => <TextField {...params} label="Integration Type" />}
            onChange={handleIntegrationTypeChange}
        />
        </Box>
        {currType && 
        <Box>
            <CurrIntegration user={user} org={org} integrationParams={integrationParams} setIntegrationParams={setIntegrationParams} />
        </Box>
        }
        {integrationParams?.credentials && 
        <Box sx={{mt: 2}}>
            <DataForm integrationType={integrationParams?.type} credentials={integrationParams?.credentials} />
        </Box>
        }
    </Box>
  );
}
