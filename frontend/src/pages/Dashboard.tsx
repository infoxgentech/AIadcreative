import React from 'react'
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material'
import {
  BrandingWatermark,
  Campaign,
  AutoAwesome,
  TrendingUp
} from '@mui/icons-material'
import { Link } from 'react-router-dom'

const Dashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <BrandingWatermark color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Brands
                  </Typography>
                  <Typography variant="h4">
                    3
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Campaign color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Active Campaigns
                  </Typography>
                  <Typography variant="h4">
                    5
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <AutoAwesome color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Content Generated
                  </Typography>
                  <Typography variant="h4">
                    42
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg. Brand Score
                  </Typography>
                  <Typography variant="h4">
                    87%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Button
                  variant="contained"
                  fullWidth
                  component={Link}
                  to="/brands"
                  startIcon={<BrandingWatermark />}
                >
                  Create New Brand
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Button
                  variant="contained"
                  fullWidth
                  component={Link}
                  to="/content"
                  startIcon={<AutoAwesome />}
                >
                  Generate Content
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Button
                  variant="outlined"
                  fullWidth
                  component={Link}
                  to="/campaigns"
                  startIcon={<Campaign />}
                >
                  Create Campaign
                </Button>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Button
                  variant="outlined"
                  fullWidth
                  href="/api/v1/content/providers/available"
                  target="_blank"
                >
                  Check AI Status
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Instagram post generated"
                  secondary="TechCorp brand • 2 hours ago"
                />
                <Chip label="Generated" color="success" size="small" />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="New brand created"
                  secondary="EcoFriendly Inc • 5 hours ago"
                />
                <Chip label="Created" color="primary" size="small" />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Campaign launched"
                  secondary="Q4 Product Launch • 1 day ago"
                />
                <Chip label="Active" color="warning" size="small" />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Email campaign content"
                  secondary="Holiday Sale • 2 days ago"
                />
                <Chip label="Approved" color="success" size="small" />
              </ListItem>
            </List>
          </Paper>
        </Grid>

        {/* AI Provider Status */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              AI Provider Status
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography>Claude AI (Primary)</Typography>
                  <Chip label="Online" color="success" />
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography>Google Gemini (Fallback)</Typography>
                  <Chip label="Online" color="success" />
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard